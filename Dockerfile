FROM python:3

WORKDIR /python-docker-project-forum-two

RUN pip3 install flask-session

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]