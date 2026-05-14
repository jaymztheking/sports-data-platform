FROM bitnami/spark:3.5

USER root

# Iceberg and AWS SDK JARs for S3/MinIO connectivity
ENV ICEBERG_VERSION=1.5.2
ENV AWS_SDK_VERSION=2.25.11

RUN curl -L -o /opt/bitnami/spark/jars/iceberg-spark-runtime-3.5_2.12-${ICEBERG_VERSION}.jar \
    https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/${ICEBERG_VERSION}/iceberg-spark-runtime-3.5_2.12-${ICEBERG_VERSION}.jar && \
    curl -L -o /opt/bitnami/spark/jars/iceberg-aws-bundle-${ICEBERG_VERSION}.jar \
    https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-aws-bundle/${ICEBERG_VERSION}/iceberg-aws-bundle-${ICEBERG_VERSION}.jar

COPY docker/spark/spark-defaults.conf /opt/bitnami/spark/conf/spark-defaults.conf

USER 1001
