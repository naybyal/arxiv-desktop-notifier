import feedparser
import webbrowser
import asyncio
import signal
import platform
from datetime import datetime, timedelta
from desktop_notifier import DesktopNotifier, Urgency, Button, ReplyField, DEFAULT_SOUND


async def wait_until_time(hour: int = 9, minute: int = 0, second: int = 0) -> timedelta:
    now = datetime.now()
    target = datetime(now.year, now.month, now.day, hour, minute)
    if now > target:
        target += timedelta(days=1)
    
    time_to_wait = (target - now).total_seconds()
    print(f"Waiting for {time_to_wait/ 3600:.2f} hours until {time_to_wait}")
    await asyncio.sleep(time_to_wait)

def get_papers(topic, start, max_results):
    feed_url = f"http://export.arxiv.org/api/query?search_query=all:{topic}&start={start}&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
    
    try:
        feed = feedparser.parse(feed_url)
        entries = [{'id': entry.id, 'title': entry.title, 'link': entry.link, 'summary': entry.summary} for entry in feed.entries]
        # print(entries)
        return entries
    except Exception as e:
        print("Error: ", e)
        return []

async def main() -> None:
    await wait_until_time(5, 53)
    notifier = DesktopNotifier(
        app_name="arXiv Notifier",
        notification_limit=10,
    )
    papers = get_papers("linux", 0, 2)
    for paper in papers:
        await notifier.send(
            title=paper['title'],
            message=f"Link : {paper['id']}",
            urgency=Urgency.Normal,
            sound=DEFAULT_SOUND,
            on_clicked=lambda: webbrowser.open_new_tab(paper['link']),
        )

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    loop.add_signal_handler(signal.SIGINT, stop_event.set)
    loop.add_signal_handler(signal.SIGTERM, stop_event.set)

    await stop_event.wait()

asyncio.run(main())