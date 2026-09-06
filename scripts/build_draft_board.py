"""Generate the published draft-board page from `fct_player_season` + `int_draft_board`.

The board is a live-draft tool, not a report: it is scanned under a pick clock, so the
page is dense, sortable, and keeps its own state. Run after a dbt build::

    uv run python -m nfl.ingest.ff_rankings          # refresh the consensus board
    NFL_DATA_DIR=data/raw NFL_DUCKDB_PATH=nfl_dev.duckdb \
      uv run dbt build --project-dir dbt_project --profiles-dir dbt_project
    uv run python scripts/build_draft_board.py

Writes a single self-contained HTML file (no external requests) which is then published
as an Artifact. Kept in version control deliberately — it was previously rebuilt from
scratch on each change, which made a one-line CSS fix a full regeneration.
"""

from __future__ import annotations

import argparse
import decimal
import json
from pathlib import Path
from typing import Any

import duckdb

DEFAULT_DB = "nfl_dev.duckdb"
DEFAULT_OUT = Path("build/draft_board.html")
SEASON = 2025
DEFAULT_SCORING = "kiddy"
ECR_CUTOFF = 200

QUERY = """
with board as (
    select *, row_number() over (order by ecr) as overall
    from dev.int_draft_board
    where player_position in ('QB', 'RB', 'WR', 'TE') and ecr <= ?
),
prod as (
    select * from dev.fct_player_season where season = ? and scoring_format = ?
),
hist as (
    select player_join_key, avg(fantasy_points_per_game) as career_ppg
    from dev.fct_player_season where scoring_format = ? group by 1
)
select b.overall, b.player_name, b.player_position, b.team, b.ecr, b.ecr_stddev,
       b.bye_week, b.scrape_date,
       f.games_played, f.fantasy_points_per_game, f.fantasy_points_floor,
       f.fantasy_points_ceiling, f.fantasy_points_stddev,
       f.value_over_ecr, h.career_ppg
from board b
left join prod f
    on b.player_join_key = f.player_join_key
    and b.player_position = f.player_position
left join hist h on b.player_join_key = h.player_join_key
order by b.ecr
"""

SCORING_LABEL = {
    "ppr": "PPR",
    "half_ppr": "Half-PPR",
    "standard": "Standard",
    "kiddy": "Kiddy league rules &mdash; standard scoring, 6-pt passing TDs",
}

FIELDS = [
    "overall",
    "player",
    "pos",
    "team",
    "ecr",
    "ecr_sd",
    "bye",
    "scraped",
    "gp",
    "ppg",
    "floor",
    "ceil",
    "sd",
    "value",
    "career_ppg",
]


def _round(x: Any, places: int = 1) -> Any:
    if isinstance(x, decimal.Decimal):
        return round(float(x), places)
    if isinstance(x, float):
        return round(x, places)
    return x


def fetch(db: str, scoring: str) -> list[dict[str, Any]]:
    con = duckdb.connect(db, read_only=True)
    rows = con.execute(QUERY, [ECR_CUTOFF, SEASON, scoring, scoring]).fetchall()
    out: list[dict[str, Any]] = []
    for row in rows:
        rec = dict(zip(FIELDS, row, strict=True))
        for key in ("ecr", "ecr_sd", "ppg", "floor", "ceil", "sd", "career_ppg"):
            rec[key] = _round(rec[key])
        rec["scraped"] = str(rec["scraped"])
        out.append(rec)
    return out


CSS = """
:root{
  --ink:#10141A;--ink-2:#171D25;--line:#252D38;--paper:#EEF0EE;
  --bg:var(--paper);--surface:#FFFFFF;--surface-2:#E7EAE7;--rule:#CBD1CC;
  --text:#161B21;--text-dim:#5C6670;--text-faint:#8A939B;
  --qb:#C2542F;--rb:#1F8467;--wr:#35689F;--te:#9C7220;
  --pos:#2C7A50;--neg:#B34334;--flat:#8A939B;--focus:#35689F;
  --mono:ui-monospace,"SF Mono",SFMono-Regular,Menlo,Consolas,monospace;
  --serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
}
@media (prefers-color-scheme:dark){:root{--bg:var(--ink);--surface:var(--ink-2);
  --surface-2:#1E2530;--rule:var(--line);--text:#E4E8EC;--text-dim:#98A3AE;
  --text-faint:#6B7681;--qb:#E2795A;--rb:#3FBF98;--wr:#6BA6DF;--te:#D9A945;
  --pos:#4FBE7C;--neg:#E0685A;--flat:#6B7681;--focus:#6BA6DF}}
:root[data-theme="dark"]{--bg:var(--ink);--surface:var(--ink-2);--surface-2:#1E2530;
  --rule:var(--line);--text:#E4E8EC;--text-dim:#98A3AE;--text-faint:#6B7681;
  --qb:#E2795A;--rb:#3FBF98;--wr:#6BA6DF;--te:#D9A945;--pos:#4FBE7C;--neg:#E0685A;
  --flat:#6B7681;--focus:#6BA6DF}
:root[data-theme="light"]{--bg:var(--paper);--surface:#FFFFFF;--surface-2:#E7EAE7;
  --rule:#CBD1CC;--text:#161B21;--text-dim:#5C6670;--text-faint:#8A939B;--qb:#C2542F;
  --rb:#1F8467;--wr:#35689F;--te:#9C7220;--pos:#2C7A50;--neg:#B34334;--flat:#8A939B;
  --focus:#35689F}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font-family:var(--mono);
  font-size:13px;line-height:1.45;-webkit-font-smoothing:antialiased;
  font-variant-numeric:tabular-nums}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px 72px}
header.masthead{padding:36px 0 18px;border-bottom:2px solid var(--text)}
.kicker{font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:var(--text-dim)}
h1{font-family:var(--serif);font-weight:600;font-size:clamp(30px,5vw,46px);line-height:1.04;
  margin:10px 0 8px;letter-spacing:-.015em;text-wrap:balance}
.dek{color:var(--text-dim);max-width:66ch;font-size:12.5px;line-height:1.6}
.dek b{color:var(--text);font-weight:600}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(126px,1fr));gap:1px;
  background:var(--rule);border:1px solid var(--rule);margin:20px 0 0}
.tile{background:var(--surface);padding:11px 13px;display:flex;flex-direction:column;gap:3px}
.tile .n{font-family:var(--serif);font-size:25px;line-height:1;font-weight:600}
.tile .l{font-size:9.5px;letter-spacing:.13em;text-transform:uppercase;color:var(--text-dim)}
.controls{display:flex;flex-wrap:wrap;gap:10px;align-items:center;padding:12px 0;
  margin-top:24px;border-bottom:1px solid var(--rule)}
.seg{display:flex;border:1px solid var(--rule);background:var(--surface)}
.seg button{font:inherit;font-size:11px;letter-spacing:.06em;background:none;border:0;
  color:var(--text-dim);padding:6px 11px;cursor:pointer;border-right:1px solid var(--rule)}
.seg button:last-child{border-right:0}
.seg button[aria-pressed="true"]{background:var(--text);color:var(--bg);font-weight:600}
button:focus-visible,input:focus-visible,tr:focus-visible{outline:2px solid var(--focus);
  outline-offset:-2px}
input[type="search"]{font:inherit;font-size:12px;background:var(--surface);color:var(--text);
  border:1px solid var(--rule);padding:6px 10px;min-width:170px}
input[type="search"]::placeholder{color:var(--text-faint)}
.act{font:inherit;font-size:11px;letter-spacing:.06em;background:var(--surface);
  border:1px solid var(--rule);color:var(--text-dim);padding:6px 11px;cursor:pointer}
.act[aria-pressed="true"]{background:var(--text);color:var(--bg);font-weight:600}
.act.danger:hover{border-color:var(--neg);color:var(--neg)}
.count{font-size:11px;color:var(--text-dim);margin-left:auto}
.count b{color:var(--text)}
/* The table owns its scroll region in both axes and the header pins to the top of it.
   Setting only overflow-x:auto forces overflow-y to auto per spec, which made a sticky
   header resolve against this wrapper instead of the viewport and park mid-table. */
.tablewrap{border:1px solid var(--rule);border-top:0;overflow:auto;max-height:70vh}
table{border-collapse:separate;border-spacing:0;width:100%;min-width:960px}
thead th{position:sticky;top:0;z-index:10;background:var(--surface-2);
  border-bottom:1px solid var(--rule);padding:0;text-align:right;white-space:nowrap}
thead th.l{text-align:left}
th button{font:inherit;font-size:9.5px;letter-spacing:.12em;text-transform:uppercase;
  color:var(--text-dim);background:none;border:0;padding:9px 8px;cursor:pointer;width:100%;
  text-align:inherit;white-space:nowrap}
th button[data-active="1"]{color:var(--text);font-weight:700}
tbody td{border-bottom:1px solid var(--rule)}
tbody tr:last-child td{border-bottom:0}
tbody tr{cursor:pointer}
tbody tr:hover td{background:var(--surface-2)}
td{padding:7px 8px;text-align:right;white-space:nowrap}
td.l{text-align:left}
.rank{color:var(--text-faint);font-size:11px;width:34px}
.pos{display:inline-block;min-width:26px;text-align:center;font-size:9.5px;font-weight:700;
  letter-spacing:.06em;padding:2px 4px;color:#fff}
.pos.QB{background:var(--qb)}.pos.RB{background:var(--rb)}
.pos.WR{background:var(--wr)}.pos.TE{background:var(--te)}
.nm{font-weight:600;font-size:12.5px}
.tm{color:var(--text-faint);font-size:10.5px;margin-left:5px}
.dim{color:var(--text-dim)}
.na{color:var(--text-faint);font-style:italic;font-size:11px}
.val{display:inline-block;min-width:38px;text-align:center;padding:2px 6px;font-size:11.5px;
  font-weight:700;border:1px solid currentColor}
.val.p{color:var(--pos)}.val.n{color:var(--neg)}.val.z{color:var(--flat)}
.rangecell{width:128px}
.range{position:relative;height:16px;width:116px;margin-left:auto}
.range .track{position:absolute;top:7px;left:0;right:0;height:2px;background:var(--rule)}
.range .span{position:absolute;top:6px;height:4px;background:currentColor;opacity:.30}
.range .dot{position:absolute;top:3px;width:2px;height:10px;background:currentColor}
.range.QB{color:var(--qb)}.range.RB{color:var(--rb)}
.range.WR{color:var(--wr)}.range.TE{color:var(--te)}
/* Drafted: struck through and dimmed, but deliberately still legible -- mid-draft you
   still need to check who went and undo a misclick. */
.pick{width:30px;padding-left:10px}
.box{width:13px;height:13px;border:1.5px solid var(--text-faint);background:none;
  padding:0;cursor:pointer;display:block;position:relative}
tr.drafted .box{background:var(--text-dim);border-color:var(--text-dim)}
tr.drafted .box::after{content:"";position:absolute;inset:2px;
  border-left:1.5px solid var(--bg);border-bottom:1.5px solid var(--bg);
  transform:rotate(-45deg) translate(1px,-1px)}
tr.drafted td{opacity:.45}
tr.drafted .nm{text-decoration:line-through}
tr.drafted:hover td{opacity:.72}
.legend{margin-top:18px;font-size:11px;color:var(--text-dim);line-height:1.7;max-width:78ch}
.legend b{color:var(--text)}
.legend ul{margin:8px 0 0;padding-left:16px}
.legend li{margin-bottom:5px}
footer{margin-top:24px;padding-top:14px;border-top:1px solid var(--rule);
  font-size:10.5px;color:var(--text-faint);line-height:1.7}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
@media (max-width:640px){.count{margin-left:0;width:100%}.tablewrap{max-height:62vh}}
"""

JS = """
const COLS=[{k:'pick',t:'',cls:'pick'},{k:'overall',t:'#'},{k:'player',t:'Player',cls:'l'},
 {k:'pos',t:'Pos',cls:'l'},{k:'bye',t:'Bye'},{k:'ecr',t:'ECR'},{k:'ppg',t:'2025 PPG'},
 {k:'range',t:'Floor-Ceiling'},{k:'sd',t:'Swing'},{k:'gp',t:'GP'},
 {k:'career_ppg',t:'Career PPG'},{k:'value',t:'Value'}];
const KEY='draftboard.v1.drafted';
let sortKey='overall',sortDir=1,posFilter='ALL',q='',hideDrafted=false;

// Persisted so a refresh mid-draft does not wipe the board. Storage can throw in a
// sandboxed frame, so every access is guarded and the page still works without it.
let drafted=new Set();
try{const raw=localStorage.getItem(KEY); if(raw) drafted=new Set(JSON.parse(raw));}catch(e){}
function save(){try{localStorage.setItem(KEY,JSON.stringify([...drafted]));}catch(e){}}
const idOf=d=>d.player+'|'+d.pos;

const maxCeil={};
DATA.forEach(d=>{if(d.ceil!=null)maxCeil[d.pos]=Math.max(maxCeil[d.pos]||0,d.ceil)});

function view(){
  let r=DATA.filter(d=>(posFilter==='ALL'||d.pos===posFilter));
  if(hideDrafted) r=r.filter(d=>!drafted.has(idOf(d)));
  if(q){const s=q.toLowerCase();
    r=r.filter(d=>d.player.toLowerCase().includes(s)||(d.team||'').toLowerCase().includes(s));}
  const k=sortKey==='range'?'ppg':(sortKey==='pick'?'overall':sortKey);
  return r.slice().sort((a,b)=>{let x=a[k],y=b[k];
    if(x==null&&y==null)return 0; if(x==null)return 1; if(y==null)return -1;
    if(typeof x==='string')return x.localeCompare(y)*sortDir;
    return (x-y)*sortDir;});
}
function num(v,d){return v==null?'<span class="na">-</span>':(d?v.toFixed(1):v)}
function valCell(v){if(v==null)return '<span class="na">-</span>';
  const c=v>0?'p':(v<0?'n':'z'); return '<span class="val '+c+'">'+(v>0?'+':'')+v+'</span>';}
function rangeCell(d){
  if(d.ppg==null)return '<span class="na">no 2025 data</span>';
  const m=maxCeil[d.pos]||1;
  const f=Math.max(0,(d.floor??0)/m*100),c=Math.min(100,(d.ceil??0)/m*100),
        p=Math.min(100,d.ppg/m*100);
  return '<div class="range '+d.pos+'"><div class="track"></div><div class="span" style="left:'
    +f+'%;width:'+Math.max(1,c-f)+'%"></div><div class="dot" style="left:'+p+'%"></div></div>';
}
function counts(){
  const total=DATA.length, gone=DATA.filter(d=>drafted.has(idOf(d))).length;
  const byPos={};
  ['QB','RB','WR','TE'].forEach(p=>{
    byPos[p]=DATA.filter(d=>d.pos===p&&!drafted.has(idOf(d))).length;});
  return {total,gone,left:total-gone,byPos};
}
function render(){
  const rows=view(), c=counts();
  document.getElementById('count').innerHTML=
    '<b>'+c.left+'</b> available &middot; '+c.gone+' drafted &middot; showing '+rows.length;
  document.getElementById('tile-left').textContent=c.left;
  document.getElementById('tile-gone').textContent=c.gone;
  document.getElementById('tb').innerHTML=rows.map(d=>{
    const on=drafted.has(idOf(d));
    return '<tr tabindex="0" data-id="'+idOf(d).replace(/"/g,'&quot;')+'"'+
      (on?' class="drafted"':'')+' aria-label="'+d.player+(on?', drafted':', available')+'">'+
      '<td class="pick"><button class="box" aria-pressed="'+on+'" tabindex="-1" '+
        'aria-label="Mark '+d.player+' drafted"></button></td>'+
      '<td class="rank">'+d.overall+'</td>'+
      '<td class="l"><span class="nm">'+d.player+'</span><span class="tm">'+(d.team||'FA')+'</span></td>'+
      '<td class="l"><span class="pos '+d.pos+'">'+d.pos+'</span></td>'+
      '<td class="dim">'+num(d.bye)+'</td><td class="dim">'+num(d.ecr,1)+'</td>'+
      '<td><strong>'+num(d.ppg,1)+'</strong></td>'+
      '<td class="rangecell">'+rangeCell(d)+'</td>'+
      '<td class="dim">'+num(d.sd,1)+'</td><td class="dim">'+num(d.gp)+'</td>'+
      '<td class="dim">'+num(d.career_ppg,1)+'</td><td>'+valCell(d.value)+'</td></tr>';
  }).join('');
  document.querySelectorAll('th button').forEach(b=>
    b.dataset.active=(b.dataset.k===sortKey)?'1':'0');
}
function toggle(id){
  if(drafted.has(id)) drafted.delete(id); else drafted.add(id);
  save(); render();
}
document.getElementById('th').innerHTML='<tr>'+COLS.map(c=>
  '<th class="'+(c.cls||'')+'">'+(c.k==='pick'?'':'<button data-k="'+c.k+'">'+c.t+'</button>')
  +'</th>').join('')+'</tr>';
document.querySelectorAll('th button').forEach(b=>b.onclick=()=>{
  const k=b.dataset.k;
  if(sortKey===k){sortDir*=-1}
  else{sortKey=k;sortDir=(k==='overall'||k==='ecr'||k==='player')?1:-1}
  render();});
// Whole row is the hit target -- a pick clock is no place for precision clicking.
const tb=document.getElementById('tb');
tb.addEventListener('click',e=>{
  const tr=e.target.closest('tr'); if(tr&&tr.dataset.id) toggle(tr.dataset.id);});
tb.addEventListener('keydown',e=>{
  if(e.key!=='Enter'&&e.key!==' ')return;
  const tr=e.target.closest('tr'); if(!tr||!tr.dataset.id)return;
  e.preventDefault(); toggle(tr.dataset.id);});
document.querySelectorAll('.seg button').forEach(b=>b.onclick=()=>{
  posFilter=b.dataset.p;
  document.querySelectorAll('.seg button').forEach(x=>x.setAttribute('aria-pressed',x===b));
  render();});
const hb=document.getElementById('hide');
hb.onclick=()=>{hideDrafted=!hideDrafted;hb.setAttribute('aria-pressed',hideDrafted);render();};
document.getElementById('reset').onclick=()=>{
  if(!drafted.size)return;
  if(confirm('Clear all '+drafted.size+' drafted players? This starts a fresh board.')){
    drafted.clear();save();render();}};
document.getElementById('q').oninput=e=>{q=e.target.value;render()};
render();
"""

PAGE = """<title>2026 Draft Board - Value vs. Consensus</title>
<style>__CSS__</style>
<div class="wrap">
<header class="masthead">
  <div class="kicker">__SCORING__ &middot; production 2022&ndash;2025 &middot; board scraped __SCRAPED__</div>
  <h1>The Draft Board</h1>
  <p class="dek">The __N__ players inside the drafted pool, ordered by expert consensus rank.
  <b>Click any row to cross a player off</b> as he is taken &mdash; it sticks through a page
  refresh. <b>Value</b> is where a player&rsquo;s 2025 production ranked at his position minus
  where he&rsquo;s being drafted; positive means he produced better than his cost.</p>
  <div class="tiles">
    <div class="tile"><span class="n" id="tile-left">__N__</span><span class="l">Available</span></div>
    <div class="tile"><span class="n" id="tile-gone">0</span><span class="l">Drafted</span></div>
    <div class="tile"><span class="n">__NPOS__</span><span class="l">Positive value</span></div>
    <div class="tile"><span class="n">__ND__</span><span class="l">No 2025 data</span></div>
    <div class="tile"><span class="n">4</span><span class="l">Seasons behind it</span></div>
  </div>
</header>
<div class="controls">
  <div class="seg" role="group" aria-label="Filter by position">
    <button data-p="ALL" aria-pressed="true">All</button>
    <button data-p="QB" aria-pressed="false">QB</button>
    <button data-p="RB" aria-pressed="false">RB</button>
    <button data-p="WR" aria-pressed="false">WR</button>
    <button data-p="TE" aria-pressed="false">TE</button>
  </div>
  <button class="act" id="hide" aria-pressed="false">Hide drafted</button>
  <button class="act danger" id="reset">Reset board</button>
  <input id="q" type="search" placeholder="Search player or team&hellip;" aria-label="Search players">
  <span class="count" id="count"></span>
</div>
<div class="tablewrap">
  <table><thead id="th"></thead><tbody id="tb"></tbody></table>
</div>
<div class="legend">
  <b>Reading it.</b>
  <ul>
    <li><b>Crossing off</b> &mdash; click a row (or focus it and hit Enter) to mark a player
      drafted. Struck-through rows stay legible on purpose: mid-draft you still need to check
      who went, and undo a misclick. <b>Hide drafted</b> collapses them; <b>Reset board</b>
      clears everything for a new draft.</li>
    <li><b>Value</b> &mdash; production rank minus draft rank, both across board members only
      so the scales are comparable. Bounded to the drafted pool; past that consensus stops
      ranking carefully and the number turns to noise.</li>
    <li><b>Floor-Ceiling</b> &mdash; 25th to 75th percentile of weekly scores, tick at the
      per-game average. Scaled within position, so bars compare RB to RB.</li>
    <li><b>Swing</b> &mdash; standard deviation of weekly scores. A 14 ppg player alternating
      4 and 24 is a different pick from one scoring 14 every week.</li>
    <li><b>no 2025 data</b> &mdash; rookies. Missing rather than zero, because zero would sort
      them last and they are unmeasured, not bad.</li>
  </ul>
</div>
<footer>
  Backward-looking by construction &mdash; second-year players read as overpriced because
  rookie usage understates a 2026 role. Consensus rank is ECR, not ADP.
  Production covers 2022&ndash;2025; the consensus board is a live snapshot, scraped __SCRAPED__.
  Cross-offs are stored in this browser only.
</footer>
</div>
<script>const DATA=__DATA__;__JS__</script>
"""


def build(data: list[dict[str, Any]], scoring: str) -> str:
    no_data = sum(1 for d in data if d["ppg"] is None)
    positive = sum(1 for d in data if d["value"] is not None and d["value"] > 0)
    scraped = data[0]["scraped"] if data else "unknown"
    return (
        PAGE.replace("__CSS__", CSS)
        .replace("__JS__", JS)
        .replace("__DATA__", json.dumps(data, separators=(",", ":")))
        .replace("__SCRAPED__", str(scraped))
        .replace("__N__", str(len(data)))
        .replace("__NPOS__", str(positive))
        .replace("__ND__", str(no_data))
        .replace("__SCORING__", SCORING_LABEL.get(scoring, scoring))
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the draft-board page")
    ap.add_argument("--db", default=DEFAULT_DB, help=f"DuckDB path (default: {DEFAULT_DB})")
    ap.add_argument(
        "--out", type=Path, default=DEFAULT_OUT, help=f"output (default: {DEFAULT_OUT})"
    )
    ap.add_argument(
        "--scoring",
        default=DEFAULT_SCORING,
        help=f"scoring_format in the mart (default: {DEFAULT_SCORING})",
    )
    args = ap.parse_args()

    data = fetch(args.db, args.scoring)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(build(data, args.scoring))
    print(f"{len(data)} players ({args.scoring}) -> {args.out} ({args.out.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
