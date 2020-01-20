import click
from apscheduler.schedulers.blocking import BlockingScheduler

import runners
from tools import parse_datetime

@click.group()
def main():
    pass

@main.command()
def scrape():
    runners.scrape()
    print("Exited successfully")

@main.command()
@click.option("--date","-d",default=None)
@click.option("--time","-t",default=None)
def enroll(date,time):
    enroller = runners.enroll_config()
    if date and time:
        datetime = parse_datetime(date,time)
        schedule = BlockingScheduler()
        schedule.add_job(runners.enroll_start, 'date', run_date=datetime, args=[enroller,schedule])
        schedule.start()
    else:
        runners.enroll_start(enroller)
    print("Exited successfully")

@main.command()
def scrape_enroll():
    runners.scrape_enroll()
    print("Exited successfully")

if __name__ == "__main__":
    main()