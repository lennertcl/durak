FROM python:buster
RUN mkdir durak
COPY .. /durak
VOLUME [ "/durak" ]
WORKDIR /durak
RUN /usr/local/bin/pip3 install -r requirements.txt 
ENV SQLALCHEMY_DATABASE_URI="sqlite:////tmp/test.db"
EXPOSE 5000
RUN mv docker-files/initializeDB.py . \
&& /usr/local/bin/python3 initializeDB.py
CMD [ "/usr/local/bin/python3", "run.py" ] 


