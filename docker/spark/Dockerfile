FROM apache/spark:3.5.6

USER root

RUN mkdir -p /opt/spark/jars

RUN curl -L \
https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/1.5.2/iceberg-spark-runtime-3.5_2.12-1.5.2.jar \
-o /opt/spark/jars/iceberg-spark-runtime.jar

RUN curl -L \
https://jdbc.postgresql.org/download/postgresql-42.7.3.jar \
-o /opt/spark/jars/postgresql.jar

RUN curl -L \
https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar \
-o /opt/spark/jars/hadoop-aws.jar

RUN curl -L \
https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar \
-o /opt/spark/jars/aws-sdk.jar

USER spark