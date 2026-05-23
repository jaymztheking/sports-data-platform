#!/bin/bash
set -e

case "$SPARK_MODE" in
  master)
    exec /opt/spark/bin/spark-class org.apache.spark.deploy.master.Master \
      --port "${SPARK_MASTER_PORT:-7077}" \
      --webui-port "${SPARK_MASTER_WEBUI_PORT:-8080}"
    ;;
  worker)
    exec /opt/spark/bin/spark-class org.apache.spark.deploy.worker.Worker \
      --webui-port "${SPARK_WORKER_WEBUI_PORT:-8081}" \
      "${SPARK_MASTER_URL:-spark://spark-master-svc:7077}"
    ;;
  *)
    exec "$@"
    ;;
esac
