FROM apache/spark:3.5.3

USER root

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Iceberg and AWS SDK JARs for S3/MinIO connectivity
ENV ICEBERG_VERSION=1.5.2

RUN curl -L -o /opt/spark/jars/iceberg-spark-runtime-3.5_2.12-${ICEBERG_VERSION}.jar \
    https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/${ICEBERG_VERSION}/iceberg-spark-runtime-3.5_2.12-${ICEBERG_VERSION}.jar && \
    curl -L -o /opt/spark/jars/iceberg-aws-bundle-${ICEBERG_VERSION}.jar \
    https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-aws-bundle/${ICEBERG_VERSION}/iceberg-aws-bundle-${ICEBERG_VERSION}.jar

COPY docker/spark/spark-defaults.conf /opt/spark/conf/spark-defaults.conf
COPY docker/spark/entrypoint.sh /opt/spark-entrypoint.sh
RUN chmod +x /opt/spark-entrypoint.sh

USER 185

ENTRYPOINT ["/opt/spark-entrypoint.sh"]
