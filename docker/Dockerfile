FROM python:3.7

ENV PROJECT_BASE_DIR /opt/app/

WORKDIR ${PROJECT_BASE_DIR}
COPY *.py ${PROJECT_BASE_DIR}/
COPY *.sh ${PROJECT_BASE_DIR}/
COPY *.txt ${PROJECT_BASE_DIR}/
COPY *.json ${PROJECT_BASE_DIR}/

RUN pip install dateparser
RUN pip install urllib3
RUN pip install pymysql

RUN chmod +x *.sh
ENTRYPOINT ["bash","start.sh"]
