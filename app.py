#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from audioop import add
import json
from os import stat
import re
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import null
from forms import *
from flask_migrate import Migrate
from datetime import date, datetime
from model import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
db.init_app(app)

# def create_app():
#   db.init_app(app)
#   return app


moment = Moment(app)
app.config.from_object('config')
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
# All models are defined in model.py



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

#  ---------------------------------------------------------------
#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = []
  for each_state_and_city in db.session.query(Venue).with_entities(Venue.state, Venue.city).distinct().all():
    state = each_state_and_city.state
    city = each_state_and_city.city
    # Constructing for all the venues
    venues = []
    for venue in db.session.query(Venue).filter(Venue.state == each_state_and_city.state).all():
      venues.append({
        'id': venue.id, 
        'name': venue.name, 
        'num_upcoming_shows': db.session.query(Show).filter(Show.venue_id == venue.id, Show.start_time>datetime.now()).count()})
    # Saving the gathered information at the end of each iteration for state
    data.append({
      'city': city, 
      'state': state, 
      'venues': venues
    })

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  response = {}
  search_word = request.form.get('search_term', '')
  db_search_result = Venue.query.filter(Venue.name.ilike('%'+search_word+'%'))
  count = db_search_result.count()
  data = []
  for venue in db_search_result.all():
    data.append({
      'id': venue.id, 
      'name': venue.name, 
      'num_upcoming_shows': db.session.query(Show).filter(Show.venue_id==venue.id, Show.start_time>datetime.now())
    })
  response['count'] = count
  response['data'] = data
  return render_template('pages/search_venues.html',  results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue_data = {}
  requested_venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
  venue_performed_show = db.session.query(Show).filter(Show.venue_id == requested_venue.id, Show.start_time<datetime.now())
  venue_upcoming_show = db.session.query(Show).filter(Show.venue_id == requested_venue.id, Show.start_time>datetime.now())
  id = requested_venue.id
  name = requested_venue.name
  # Formatting and preparing the genres for presentation
  genres = requested_venue.genres.split(',')
  genres.pop()  # Removing the last empty string
  address = requested_venue.address
  city = requested_venue.city
  state = requested_venue.state
  phone = requested_venue.phone
  website = requested_venue.website
  facebook_link = requested_venue.facebook_link
  seeking_talent = requested_venue.seeking_talent == True # Boolean expression
  image_link = requested_venue.image_link

  past_shows = []
  for performed_show in venue_performed_show.all():
      performed_show_artist = db.session.query(Artist).join(Show).filter(Show.artist_id == performed_show.artist_id).first()
      past_shows.append({
        'artist_id': performed_show_artist.id, 
        'artist_name': performed_show_artist.name, 
        'artist_image_link': performed_show_artist.image_link, 
        'start_time': str(performed_show.start_time)
      })

  upcoming_shows = []
  for upcoming_show in venue_upcoming_show.all():
      upcoming_show_artist = db.session.query(Artist).join(Show).filter(Show.artist_id == upcoming_show.artist_id).first()
      upcoming_shows.append({
        'artist_id': upcoming_show_artist.id, 
        'artist_name': upcoming_show_artist.name, 
        'artist_image_link': upcoming_show_artist.image_link, 
        'start_time': str(upcoming_show.start_time)
      })
  past_shows_count = venue_performed_show.count()
  upcoming_shows_count = venue_upcoming_show.count()
  # Adding all the collected data to the mock up structure
  venue_data['id'] = id
  venue_data['name'] = name
  venue_data['genres'] = genres
  venue_data['address'] = address
  venue_data['city'] = city
  venue_data['state'] = state
  venue_data['phone'] = phone
  venue_data['website'] = website
  venue_data['facebook_link'] = facebook_link
  venue_data['seeking_talent'] = seeking_talent
  venue_data['image_link'] = image_link
  venue_data['past_shows'] = past_shows
  venue_data['upcoming_shows'] = upcoming_shows
  venue_data['past_shows_count'] = past_shows_count
  venue_data['upcoming_shows_count'] = upcoming_shows_count
  
  data = list(filter(lambda d: d['id'] == venue_id, [venue_data]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  ----------------------------------------------------------------
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # Formatting genres before adding it to the DB
  genres = ''
  data_length = len(request.form.getlist('genres'))
  for genre_index in range(data_length):
    genres += str(request.form.getlist('genres')[genre_index])+","

  # Formatting value, supplied by talent seeking field
  seeking_talent = False
  if request.form.get('seeking_talent') == 'y':
    seeking_talent = True
  else:
    seeking_talent = False

  try:
    form = Venue(
    name = request.form.get('name'),
    city = request.form.get('city'),
    state = request.form.get('state'),
    address = request.form.get('address'),
    phone = str(request.form.get('phone')),
    image_link = request.form.get('image_link'),
    facebook_link = request.form.get('facebook_link'),
    genres = genres,
    seeking_talent = seeking_talent,
    seeking_description = request.form.get('seeking_description'),
    website = request.form.get('website_link') 
  )
     
    db.session.add(form)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occured. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
  venue = Venue.query.get(venue_id)
  try:
    db.session.delete(venue)
    db.session.commit()
    flash('Venue was deleted successfully.')
  except:
    db.session.rollback()
    flash('There was an error. Venue was not deleted.')
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template(url_for('venues'))

#  ----------------------------------------------------------------
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  data = []
  for artist in db.session.query(Artist).all():
    id = artist.id
    name = artist.name
    data.append({
      'id': id, 
      'name': name
    })

  return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  response = {}
  search_word = request.form.get('search_term', '')
  db_search_result = Artist.query.filter(Artist.name.ilike('%'+search_word+'%'))
  count = db_search_result.count()
  data = []
  # Getting and saving all artist that match up with the searched keyword
  for artist in db_search_result.all():
    data.append({
      'id': artist.id, 
      'name': artist.name, 
      'num_upcoming_shows': db.session.query(Show).filter(Show.artist_id==artist.id, Show.start_time>datetime.now())
    })
  response['count'] = count
  response['data'] = data
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist_data = {}
  requested_artist = db.session.query(Artist).filter(Artist.id == artist_id).first()
  artist_performed_show = db.session.query(Show).filter(Show.artist_id == requested_artist.id, Show.start_time<datetime.now())
  artist_upcoming_show = db.session.query(Show).filter(Show.artist_id == requested_artist.id, Show.start_time>datetime.now())
  id = requested_artist.id
  name = requested_artist.name
  # Formatting and preparing the genres so that the genres is okay for presentation
  genres = requested_artist.genres.split(',')
  genres.pop()
  city = requested_artist.city
  state = requested_artist.state
  phone = requested_artist.phone
  seeking_venue = requested_artist.seeking_venue == True
  image_link = requested_artist.image_link
  past_shows = [] # Obtaining and saving data for past shows
  for performed_show in artist_performed_show.all():
    performed_show_venue = db.session.query(Venue).join(Show).filter(Show.venue_id == performed_show.venue_id).first()
    past_shows.append({
      'venue_id': performed_show_venue.id, 
      'venue_name': performed_show_venue.name, 
      'venue_image_link': performed_show_venue.image_link, 
      'start_time': str(performed_show.start_time)
    })
  upcoming_shows = [] # Obtaining and saving data for upcoming shows
  for upcoming_show in artist_upcoming_show.all():
    upcoming_show_venue = db.session.query(Venue).join(Show).filter(Show.venue_id == upcoming_show.venue_id).first()
    upcoming_shows.append({
      'venue_id': upcoming_show_venue.id, 
      'venue_name': upcoming_show_venue.name,
      'venue_image_link': upcoming_show_venue.image_link, 
      'start_time': str(upcoming_show.start_time)
    })
  past_shows_count = artist_performed_show.count()
  upcoming_shows_count = artist_upcoming_show.count()
  # Adding all the data to mocked up structure
  artist_data['id'] = id
  artist_data['name'] = name
  artist_data['genres'] = genres
  artist_data['city'] = city
  artist_data['state'] = state
  artist_data['phone'] = phone
  artist_data['seeking_venue'] = seeking_venue
  artist_data['image_link'] = image_link
  artist_data['past_shows'] = past_shows
  artist_data['upcoming_shows'] = upcoming_shows
  artist_data['past_shows_count'] = past_shows_count
  artist_data['upcoming_shows_count'] = upcoming_shows_count


  data = list(filter(lambda d: d['id'] == artist_id, [artist_data]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  ----------------------------------------------------------------
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist_record = Artist.query.get(artist_id)
  # Formating genres
  genres_list = artist_record.genres.split(',')
  genres_list.pop()
  # Converting the genres back into set so that it can fit in for the SelectMultipleField
  genres = set(genres_list)
  form = ArtistForm()
  artist={
    "id": artist_record.id,
    "name": artist_record.name,
    "genres": genres,
    "city": artist_record.city,
    "state": artist_record.state,
    "phone": artist_record.phone,
    "website": artist_record.website,
    "facebook_link": artist_record.facebook_link,
    "seeking_venue": artist_record.seeking_venue,
    "seeking_description": artist_record.seeking_description,
    "image_link": artist_record.image_link
  }
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  # Parsing (reformatting) genres data
  genres = ''
  data_length = len(request.form.getlist('genres'))
  for index in range(data_length):
    genres += str(request.form.getlist('genres')[index])+","
  # Taking & storing data from each of the fields
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  phone = request.form.get('phone')
  image_link = request.form.get('image_link')
  facebook_link = request.form.get('facebook_link')
  website = request.form.get('website_link')
  seeking_venue = request.form.get('seeking_venue')
  seeking_description = request.form.get('seeking_description')

  # Updating artist's record
  try:
    artist.name = name
    artist.city = city
    artist.state = state
    artist.phone = phone
    artist.genre = genres
    artist.image_link = image_link
    artist.facebook_link = facebook_link
    artist.website = website
    artist.seeking_venue = seeking_venue
    artist.seeking_description = seeking_description
    # Applying the changes to the DB table
    db.session.commit()
  except:
    db.session.rollback()
    flash('There was an error. Artist\'s record  update was not successful.')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue_record = Venue.query.get(venue_id)
  # Formatting genres
  genres_list = venue_record.genres.split(',')
  genres_list.pop()
  # Converting the genres back into set so that it can fit in for the SelectMultipleField
  genres = set(genres_list)
  form = VenueForm()
  venue={
    "id": venue_record.id,
    "name": venue_record.name,
    "genres": genres,
    "address": venue_record.address,
    "city": venue_record.city,
    "state": venue_record.state,
    "phone": venue_record.phone,
    "website": venue_record.website,
    "facebook_link": venue_record.facebook_link,
    "seeking_talent": venue_record.seeking_talent,
    "seeking_description": venue_record.seeking_description,
    "image_link": venue_record.image_link
  }
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)
  # Parsing (reformatting) genres data
  genres = ''
  data_length = len(request.form.getlist('genres'))
  for index in range(data_length):
    genres += str(request.form.getlist('genres')[index])+","
  # Taking data from all fields
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  address = request.form.get('address')
  phone = request.form.get('phone')
  facebook_link = request.form.get('facebook_link')
  image_link = request.form.get('image_link')
  website = request.form.get('website')
  seeking_talent = request.form.get('seeking_talent')
  seeking_description = request.form.get('seeking_description')
  # Updating venue's record
  try:
    venue.name = name
    venue.city = city
    venue.state = state
    venue.address = address
    venue.phone = phone
    venue.genres = genres
    venue.facebook_link = facebook_link
    venue.image_link = image_link
    venue.website = website
    venue.seeking_talent = seeking_talent
    venue.seeking_description = seeking_description
    # Applying the changes to the DB table
    db.session.commit()
  except:
    db.session.rollback()
    flash('There was an error. Venue\'s record update was not successful.')
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  ----------------------------------------------------------------
#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  genres = ''
  data_length = len(request.form.getlist('genres'))
  for genre_index in range(data_length):
    genres += str(request.form.getlist('genres')[genre_index])+","
  
  # Formatting value, supplied by venue seeking field
  seeking_venue = False
  if request.form.get('seeking_venue') == 'y':
    seeking_venue = True
  else:
    seeking_venue = False

  try:   
    form = Artist(
      name = request.form.get('name'),
      city = request.form.get('city'),
      state = request.form.get('state'),
      phone = request.form.get('phone'),
      genres = genres,
      image_link = request.form.get('image_link'),
      facebook_link = request.form.get('facebook_link'),
      website = request.form.get('website_link'),
      seeking_venue = seeking_venue,
      seeking_description = request.form.get('seeking_description')
    )
    db.session.add(form)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occured. Artist ' + request.form['name'] + ' could not be listed')
  finally:
    db.session.close()

  return render_template('pages/home.html')

#  ----------------------------------------------------------------
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = []
  all_shows = db.session.query(Show).all()
  for each_show in all_shows:
    each_show_venue = db.session.query(Venue).join(Show).filter(Show.venue_id == each_show.venue_id).first()
    each_show_artist = db.session.query(Artist).join(Show).filter(Show.artist_id == each_show.artist_id).first()
    data.append({
      'venue_id': each_show_venue.id, 
      'venue_name': each_show_venue.name, 
      'artist_id': each_show_artist.id, 
      'artist_name': each_show_artist.name, 
      'artist_image_link': each_show_artist.image_link, 
      'start_time': str(each_show.start_time)
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
  try:
    form = Show(
      artist_id = request.form.get('artist_id'),
      venue_id = request.form.get('venue_id'),
      start_time = request.form.get('start_time')
    )

    db.session.add(form)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occured. Show could not be listed')
  finally:
    db.session.close()
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