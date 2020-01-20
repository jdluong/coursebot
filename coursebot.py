import click
from apscheduler.schedulers.blocking import BlockingScheduler

import run
from tools import parse_datetime

@click.group()
def main():
    pass

@main.command()
def scrape():
    run.scrape()
    print("Exited successfully")

@main.command()
@click.option("--date","-d",default=None)
@click.option("--time","-t",default=None)
def enroll(date,time):
    enroller = run.enroll_config()
    if date and time:
        datetime = parse_datetime(date,time)
        schedule = BlockingScheduler()
        schedule.add_job(run.enroll_start, 'date', run_date=datetime, args=[enroller,schedule])
        schedule.start()
    else:
        run.enroll_start(enroller)
    print("Exited successfully")

@main.command()
def scrape_enroll():
    run.scrape_enroll()
    print("Exited successfully")

if __name__ == "__main__":
    main()