#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from cmath import log
from email.policy import default
import json
import sys
from tkinter.messagebox import NO
from typing import overload
from urllib import response
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from flask_migrate import Migrate
import collections
from models import db, Artist, Show, Venue
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#


app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)
app.config['SECRET_KEY']
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:drimms19@localhost:5432/alx'
collections.Callable = collections.abc.Callable
#SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:drimms19@localhost:5432/alx'
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    venues = Venue.query.order_by(Venue.state, Venue.city, Venue.id).all()
    #print(venues)
    data = [ucs.filter_on_city_state for ucs in venues]
    #print(data)
    
    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term')
  venues = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()
  data = []
  for venue in venues:
      tmp = {}
      tmp['id'] = venue.id
      tmp['name'] = venue.name
      tmp['num_upcoming_shows'] = len(venue.shows)
      data.append(tmp)
  response = {}
  response['count'] = len(data)
  response['data'] = data

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')

def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    def fix_json_array(obj, attr):
      arr = getattr(obj, attr)
      if isinstance(arr, list) and len(arr) > 1 and arr[0] == '{':
          arr = arr[1:-1]
          arr = "".join(arr).split(",")

          setattr(obj,attr, arr)
    fix_json_array(venue, "genres")
    #print(venue.genres)
    past_shows = list(filter(lambda x: x.start_time < datetime.today(), venue.shows))
    upcoming_shows = list(filter(lambda x: x.start_time >= datetime.today(), venue.shows))

    past_shows = list(map(lambda x: x.show_artist(), past_shows))
    upcoming_shows = list(map(lambda x: x.show_artist(), upcoming_shows))
    data = venue.to_dict()
    data['past_shows'] = past_shows
    data['upcoming_shows'] = upcoming_shows
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)

    return render_template('pages/show_venue.html', venue=data)

  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
    error = False
    form = VenueForm()
    venue = Venue()
    def fix_json_array(obj, attr):
      arr = getattr(obj, attr)
      if isinstance(arr, list) and len(arr) > 1 and arr[0] == '{':
          arr = arr[1:-1]
          arr = ''.join(arr).split(",")
          setattr(obj,attr, arr)
    fix_json_array(request.form['phone'], "genres")
    print(venue)
    if form.validate_on_submit:
      try:
        
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        venue.genres = request.form.getlist('genres')
        #venue.genres = 
        #print(venue.phone)
        #venue.genres = "', ".join(tmp_genres)
        venue.facebook_link = request.form['facebook_link']
        if venue.phone.isdigit():
          db.session.add(venue)
          db.session.commit()
        else :
          error = True
          db.session.rollback()
          flash('Error, phone number :' + request.form['phone'] +  ' must be in format xxx-xxx-xxxx"')
      except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
      finally:
        db.session.close()
        if error:
          flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        else:
        
          flash('Venue ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')
    else:
      flash('An error occurred an form is not valid')
  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., 
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  
  return render_template('pages/artists.html', artists=Artist.query.all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
  
  search_term = request.form.get('search_term')
  search_result = Artist.query.filter(
    Artist.name.ilike('%{}%'.format(search_term))).all()
  response = {}
  response['count'] = len(search_result)
  response['data'] = search_result
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  def fix_json_array(obj, attr):
      arr = getattr(obj, attr)
      if isinstance(arr, list) and len(arr) > 1 and arr[0] == '{':
          arr = arr[1:-1]
          arr = ''.join(arr).split(",")
          setattr(obj,attr, arr)
  fix_json_array(artist, "genres")
  
  past_shows = list(filter(lambda d: d.start_time < datetime.today(), artist.shows))
  upcoming_shows = list(filter(lambda d: d.start_time >= datetime.today(), artist.shows))
  past_shows = list(map(lambda d: d.show_venue(), past_shows))
  upcoming_shows = list(map(lambda d: d.show_venue(), upcoming_shows))
  
  data = artist.to_dict()

  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows) 
  return render_template('pages/show_artist.html', artist=data)
  #data = list(filter(lambda d: d['id'] == artist_id, [artist]))[0]

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.get(artist_id)
    error = False
    try:
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        tmp_genres = request.form.getlist('genres')
        artist.genres = ','.join(tmp_genres)
        artist.website_link = request.form['website_link']
        artist.image_link = request.form['image_link']
        artist.facebook_link = request.form['facebook_link']
        artist.seeking_description = request.form['seeking_description']
        if artist.phone.isdigit():
          db.session.add(artist)
          db.session.commit()
        else :
          error = True
          db.session.rollback()
          flash('Error, phone number :' + request.form['phone'] + ' ' +  ' must be in format xxx-xxx-xxxx"')
       
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
          flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
        else:
          flash('Artist ' + request.form['name'] + ' was successfully updated!')
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)
  error = False
  try:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    tmp_genres = request.form.getlist('genres')
    venue.genres = ','.join(tmp_genres)  
    venue.facebook_link = request.form['facebook_link']
    if venue.phone.isdigit():
          db.session.add(venue)
          db.session.commit()
    else :
      error = True
      db.session.rollback()
      flash('Error, phone number :' + request.form['phone'] + ' ' +  ' is not valid' +  ' must be in format xxx-xxx-xxxx')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info)
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
    else:
      flash('Venue ' + request.form['name'] + ' was successfully updated!')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm()
    error = False
    artist = Artist()

    try:
        
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        print(artist.phone.isdigit())
        artist.genres= request.form.getlist('genres')
        #artist.genres = ','.join(tmp_genres)
        artist.website_link = request.form['website_link']
        artist.image_link = request.form['image_link']
        artist.facebook_link = request.form['facebook_link']
        artist.seeking_description = request.form['seeking_description']

        if artist.phone.isdigit():
          db.session.add(artist)
          db.session.commit()
        else :
          error = True
          db.session.rollback()
          flash('Error, phone number :' + request.form['phone'] +  ' must be in format xxx-xxx-xxxx"')
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Artist ' +
                  request.form['name'] + ' could not be listed.')
        else:
            flash('Artist ' + request.form['name'] +
                  ' was successfully listed!')
        return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.all()
  data = []
  for show in shows:
    data.append({
        'venue_id': show.venue.id,
        'venue_name': show.venue.name,
        'artist_id': show.artist.id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.start_time.isoformat()
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  try:
    show = Show()
    show.artist_id = request.form['artist_id']
    show.venue_id = request.form['venue_id']
    show.start_time = request.form['start_time']
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info)
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Show could not be listed.')
    else:
      flash('Show was successfully listed!')

  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
