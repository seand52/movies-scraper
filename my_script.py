from bs4 import BeautifulSoup
from requests_html import HTMLSession
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
import json

session = HTMLSession()
my_email = ''
password = ''
receiver_email = ['seand52@gmail.com']


# Get environment variables from secrets.json file
with open('secrets.json') as json_file:
    data = json.load(json_file)
    my_email = data['myEmail']
    password = data['myPassword']


def get_times(movie):
    times = movie.select('.cartelerascont .showtimes a')
    times_arr = []
    for item in times[1:]:
        times_arr.append(item.text.strip())
    return times_arr


def get_data():
    url = 'https://www.ecartelera.com/cines/95,0,1.html'
    resp = session.get(url)
    resp.html.render(timeout=10, sleep=10)
    html_soup = BeautifulSoup(resp.html.html, 'html.parser')
    movies = html_soup.find_all('div', class_='lfilmbc cajax')
    return movies


def get_cast(movie):
    cast = movie.find_all("p", class_="cast")
    actors_array = []
    for item in cast:
        actors = item.select('a')
        for actor in actors:
            actors_array.append(actor.text)
    return actors_array


def get_movie_details(movie):
    name = movie.select('h4  span')[0].text
    duration = movie.select(
        '.info span:nth-of-type(1)')[0].previous_sibling.strip()
    country = movie.select(
        '.info span:nth-of-type(2)')[0].previous_sibling.strip()
    genre = movie.select(
        '.info span:nth-of-type(3)')[0].previous_sibling.strip()
    return name, duration, country, genre


def make_email_template(data):
    message = MIMEMultipart("alternative")
    message["Subject"] = "Movies of the week"
    message["From"] = my_email
    message["To"] = ', '.join(receiver_email)
    output = ""
    for item in data:
        output = output + (
            f"""\
                <li>
                    <strong>{item['name']}</strong>:
                        <ul>
                            <li>
                                Show times: {', '.join(item['show_times'])}
                            </li>
                            <li>
                                Actors: {', '.join(item['cast'])}
                            </li>
                            <li>
                                Genre: {item['genre']}
                            </li>
                        </ul>
                </li>"""
        )
    html = """\
        <html>
            <body>
            <p>These are the movies for the weekend:</p>
            <ul>
            {0}
            </ul>
            </body>
        </html>
        """
    part1 = MIMEText(html.format(output), "html")
    message.attach(part1)
    return message


def send_email(template):
    template = format(template).encode('utf-8')
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(my_email, password)
        server.sendmail(my_email, receiver_email, template)


def main():
    details = []
    movies = get_data()
    for index, movie in enumerate(movies):
        name, duration, country, genre = get_movie_details(movie)
        actors = get_cast(movie)
        times = get_times(movie)
        details.append({
            'name': name,
            'duration': duration,
            'country': country,
            'genre': genre,
            'cast': actors,
            'show_times': times
        })
    template = make_email_template(details)
    send_email(template)
    return 'ok'


main()
