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
moment = Moment(app)
app.config.from_object('config')
db.init_app(app=app)
migrate = Migrate(app, db)
today_time = datetime.now()


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


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

  venue1 = Venue.query.get(1)
  venue1_past_shows_count = Show.query.filter_by(venue_id=venue1.id).filter( Show.start_time<today_time).count()
  venue2 = Venue.query.get(3)
  venue2_upcoming_shows_count = Show.query.filter_by(venue_id=venue2.id).filter(Show.start_time>today_time).count()
  venue3 = Venue.query.get(2)
  venue3_upcoming_shows_count = Show.query.filter_by(venue_id=venue3.id).filter(Show.start_time>today_time).count()
  data=[{
    "city": venue1.city,
    "state": venue1.state,
    "venues": [{
      "id": venue1.id,
      "name": venue1.name,
      "num_upcoming_shows": venue1_past_shows_count,
    }, {
      "id": venue2.id,
      "name": venue2.name,
      "num_upcoming_shows": venue2_upcoming_shows_count
    }]
  }, {
    "city": venue3.city,
    "state": venue3.state,
    "venues": [{
      "id": venue3.id,
      "name": venue3.name,
      "num_upcoming_shows": venue3_upcoming_shows_count
    }]
  }]
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_word = request.form.get('search_term', '')

  db_search_result = Venue.query.filter(Venue.name.ilike('%'+search_word+'%'))

  response={
    "count": db_search_result.count(),
    "data": [{
      "id": db_search_result.first().id,
      "name": db_search_result.first().name,
      "num_upcoming_shows": Show.query.filter(Show.artist_id == db_search_result.first().id, Show.start_time > today_time).count()
    }]
  }
  return render_template('pages/search_venues.html',  results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue1 = Venue.query.get(1)
  venue1_genres = venue1.genres.split(',')
  venue1_artist = Artist.query.get(4)
  venue1_show_time = str(Show.query.get(1).start_time)
  venue1_past_shows_count = Show.query.filter(Show.venue_id == venue1.id, Show.start_time < today_time).count()
  venue1_upcoming_shows_count = Show.query.filter(Show.venue_id == venue1.id, Show.start_time > today_time).count()
  venue1_upcoming_shows = Show.query.filter(Show.venue_id == venue1.id, Show.start_time > today_time).all()
 

  venue2 = Venue.query.get(2)
  venue2_genres = venue2.genres.split(',')
  venue2_past_shows_count = Show.query.filter(Show.venue_id == venue2.id, Show.start_time < today_time).count()
  venue2_upcoming_shows_count = Show.query.filter(Show.venue_id == venue2.id, Show.start_time > today_time).count()
  venue2_upcoming_shows = Show.query.filter(Show.venue_id == venue2.id, Show.start_time > today_time).all()
  venue2_past_shows = Show.query.filter(Show.venue_id == venue2.id, Show.start_time < today_time).all()


  venue3 = Venue.query.get(3)
  venue3_genres = venue3.genres.split(',')
  venue3_1st_artist = Artist.query.get(5)
  venue3_2nd_artist = Artist.query.get(6)
  venue3_show_time = str(Show.query.get(2).start_time)
  venue3_2nd_show_time = str(Show.query.get(3).start_time)
  venue3_3rd_show_time = str(Show.query.get(4).start_time)
  venue3_4th_show_time = str(Show.query.get(5).start_time)
  venue3_past_shows_count = Show.query.filter(Show.venue_id == venue3.id, Show.start_time < today_time).count()
  venue3_upcoming_shows_count = Show.query.filter(Show.venue_id == venue3.id, Show.start_time > today_time).count()
  
  data1={
    "id": venue1.id,
    "name": venue1.name,
    "genres": venue1_genres,
    "address": venue1.address,
    "city": venue1.city,
    "state": venue1.state,
    "phone": venue1.phone,
    "website": venue1.website,
    "facebook_link": venue1.facebook_link,
    "seeking_talent": venue1.seeking_talent,
    "seeking_description": venue1.seeking_description,
    "image_link": venue1.image_link,
    "past_shows": [{
      "artist_id": venue1_artist.id,
      "artist_name": venue1_artist.name,
      "artist_image_link": venue1_artist.image_link,
      "start_time":  venue1_show_time
    }],
    "upcoming_shows": venue1_upcoming_shows,
    "past_shows_count": venue1_past_shows_count,
    "upcoming_shows_count": venue1_upcoming_shows_count,
  }
  data2={
    "id": venue2.id,
    "name": venue2.name,
    "genres": venue2_genres,
    "address": venue2.address,
    "city": venue2.city,
    "state": venue2.state,
    "phone": venue2.phone,
    "website": venue2.website,
    "facebook_link": venue2.facebook_link,
    "seeking_talent": venue2.seeking_talent,
    "image_link": venue2.image_link,
    "past_shows": venue2_past_shows,
    "upcoming_shows": venue2_upcoming_shows,
    "past_shows_count": venue2_past_shows_count,
    "upcoming_shows_count": venue2_upcoming_shows_count,
  }
  data3={
    "id": venue3.id,
    "name": venue3.name,
    "genres": venue3_genres,
    "address": venue3.address,
    "city": venue3.city,
    "state": venue3.state,
    "phone": venue3.phone,
    "website": venue3.website,
    "facebook_link": venue3.facebook_link,
    "seeking_talent": venue3.seeking_talent,
    "image_link": venue3.image_link,
    "past_shows": [{
      "artist_id": venue3_1st_artist.id,
      "artist_name": venue3_1st_artist.name,
      "artist_image_link": venue3_1st_artist.image_link,
      "start_time": venue3_show_time
    }],
    "upcoming_shows": [{
      "artist_id": venue3_2nd_artist.id,
      "artist_name": venue3_2nd_artist.name,
      "artist_image_link": venue3_2nd_artist.image_link,
      "start_time": venue3_2nd_show_time
    }, {
      "artist_id": venue3_2nd_artist.id,
      "artist_name": venue3_2nd_artist.name,
      "artist_image_link": venue3_2nd_artist.image_link,
      "start_time": venue3_3rd_show_time
    }, {
      "artist_id": venue3_2nd_artist.id,
      "artist_name": venue3_2nd_artist.name,
      "artist_image_link": venue3_2nd_artist.image_link,
      "start_time": venue3_4th_show_time
    }],
    "past_shows_count": venue3_past_shows_count,
    "upcoming_shows_count": venue3_upcoming_shows_count,
  }
  data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  
  genres = ''
  data_length = len(request.form.getlist('genres'))
  for data in range(data_length):
    genres += str(request.form.getlist('genres')[data])+","

  try:
    form = Venue(
    name = request.form.get('name'),
    city = request.form.get('city'),
    state = request.form.get('state'),
    address = request.form.get('address'),
    phone = request.form.get('phone'),
    image_link = request.form.get('image_link'),
    facebook_link = request.form.get('facebook_link'),
    genres = genres,
    seeking_talent = request.form.get('seeking_talent'),
    seeking_description = request.form.get('seeking_description'),
    website_link = request.form.get('website_link') 
  )
     
    db.session.add(form)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occured. Venue ' + request.form['name'] + ' could not be listed.' + '' + 'after the empty string')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

  venue = Venue.query.get(venue_id)
  try:
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
    flash('There was an error. Venue was not deleted.')
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template(url_for('venues'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artist1 = Artist.query.get(4)
  artist2 = Artist.query.get(5)
  artist3 = Artist.query.get(6)
  data=[{
    "id": artist1.id,
    "name": artist1.name,
  }, {
    "id": artist2.id,
    "name": artist2.name,
  }, {
    "id": artist3.id,
    "name": artist3.name,
  }]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_word = request.form.get('search_term', '')

  db_search_result = Artist.query.filter(Artist.name.ilike('%'+search_word+'%'))

  response={
    "count": db_search_result.count(),
    "data": [{
      "id": db_search_result.first().id,
      "name": db_search_result.first().name,
      "num_upcoming_shows": Show.query.filter(Show.artist_id == db_search_result.first().id, Show.start_time > today_time).count(),
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist4 = Artist.query.get(4)
  artist4_genres = artist4.genres.split(',')
  artist4_genres.remove('')
  artist4_venue = Venue.query.get(1)
  artist4_show_time = str(Show.query.get(1).start_time)
  artist4_past_shows_count = Show.query.filter_by(artist_id=artist4.id).filter(Show.start_time<today_time).count()
  artist4_upcoming_shows_count = Show.query.filter_by(artist_id=artist4.id).filter(Show.start_time>today_time).count()
  artist4_upcoming_shows = Show.query.filter_by(artist_id=artist4.id).filter(Show.start_time>today_time)

  artist5 = Artist.query.get(5)
  artist5_genres = artist5.genres.split(',')
  artist5_genres.remove('')
  artist5_venue = Venue.query.get(3)
  artist5_show_time = str(Show.query.get(2).start_time)
  artist5_past_shows_count = Show.query.filter_by(artist_id=artist5.id).filter(Show.start_time<today_time).count()
  artist5_upcoming_shows_count = Show.query.filter_by(artist_id=artist5.id).filter(Show.start_time>today_time).count()
  artist5_upcoming_shows = Show.query.filter_by(artist_id=artist5.id).filter(Show.start_time>today_time)

  artist6 = Artist.query.get(6)
  artist6_genres = artist6.genres.split(',')
  artist6_genres.remove('')
  artist6_venue = Venue.query.get(3)
  artist6_1st_show_time = str(Show.query.get(3).start_time)
  artist6_2nd_show_time = str(Show.query.get(4).start_time)
  artist6_3rd_show_time = str(Show.query.get(5).start_time)
  artist6_past_shows_count = Show.query.filter_by(artist_id=artist6.id).filter(Show.start_time<today_time).count()
  artist6_upcoming_shows_count = Show.query.filter_by(artist_id=artist6.id).filter(Show.start_time>today_time).count()
  artist6_upcoming_shows = Show.query.filter_by(artist_id=artist6.id).filter(Show.start_time>today_time)


  data1={
    "id": artist4.id,
    "name": artist4.name,
    "genres": artist4_genres,
    "city": artist4.city,
    "state": artist4.state,
    "phone": artist4.phone,
    "website": artist4.website,
    "facebook_link": artist4.facebook_link,
    "seeking_venue": artist4.seeking_venue,
    "seeking_description": artist4.seeking_description,
    "image_link": artist4.image_link,
    "past_shows": [{
      "venue_id": artist4_venue.id,
      "venue_name": artist4_venue.name,
      "venue_image_link": artist4_venue.image_link,
      "start_time": artist4_show_time
    }],
    "upcoming_shows": artist4_upcoming_shows,
    "past_shows_count": artist4_past_shows_count,
    "upcoming_shows_count": artist4_upcoming_shows_count,
  }
  data2={
    "id": artist5.id,
    "name": artist5.name,
    "genres": artist5_genres,
    "city": artist5.city,
    "state": artist5.state,
    "phone": artist5.phone,
    "facebook_link": artist5.facebook_link,
    "seeking_venue": artist5.seeking_venue,
    "image_link": artist5.image_link,
    "past_shows": [{
      "venue_id": artist5_venue.id,
      "venue_name": artist5_venue.name,
      "venue_image_link": artist5_venue.image_link,
      "start_time": artist5_show_time
    }],
    "upcoming_shows": artist5_upcoming_shows,
    "past_shows_count": artist5_past_shows_count,
    "upcoming_shows_count": artist5_upcoming_shows_count,
  }
  data3={
    "id": artist6.id,
    "name": artist6.name,
    "genres": artist6_genres,
    "city": artist6.city,
    "state": artist6.city,
    "phone": artist6.phone,
    "seeking_venue": artist6.seeking_venue,
    "image_link": artist6.image_link,
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": artist6_venue.id,
      "venue_name": artist6_venue.name,
      "venue_image_link": artist6_venue.image_link,
      "start_time": artist6_1st_show_time
    }, {
      "venue_id": artist6_venue.id,
      "venue_name": artist6_venue.name,
      "venue_image_link": artist6_venue.image_link,
      "start_time": artist6_2nd_show_time
    }, {
      "venue_id": artist6_venue.id,
      "venue_name": artist6_venue.name,
      "venue_image_link": artist6_venue.image_link,
      "start_time": artist6_3rd_show_time
    }],
    "past_shows_count": artist6_past_shows_count,
    "upcoming_shows_count": artist6_upcoming_shows_count,
  }
  data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist_record = Artist.query.get(artist_id)
  # Formating genres
  genres_list = artist_record.genres.split(',')
  genres_list.remove('')
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
  # TODO: populate form with fields from artist with ID <artist_id> - done
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)

  # Parsing (reformatting) genres data
  genres = ''
  data_length = len(request.form.getlist('genres'))
  for data in range(data_length):
    genres += str(request.form.getlist('genres')[data])+","

  # Taking data from each field
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
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)

  # Parsing (reformatting) genres data
  genres = ''
  data_length = len(request.form.getlist('genres'))
  for data in range(data_length):
    genres += str(request.form.getlist('genres')[data])+","
  
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
  for data in range(data_length):
    genres += str(request.form.getlist('genres')[data])+","
  
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
      seeking_venue = request.form.get('seeking_venue'),
      seeking_description = request.form.get('seeking_description')
    )

    db.session.add(form)
    db.session.commit()

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occured. Artist ' + request.form['name'] + ' could not be listed')
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  venue1 = Venue.query.get(1)
  venue3 = Venue.query.get(3)
  artist4 = Artist.query.get(4)
  artist5 = Artist.query.get(5)
  artist6 = Artist.query.get(6)
  data=[{
    "venue_id": venue1.id,
    "venue_name": venue1.name,
    "artist_id": artist4.id,
    "artist_name": artist4.name,
    "artist_image_link": artist4.image_link,
    "start_time": str(Show.query.get(1).start_time)
  }, {
    "venue_id": venue3.id,
    "venue_name": venue3.name,
    "artist_id": artist5.id,
    "artist_name": artist5.name,
    "artist_image_link": artist5.image_link,
    "start_time": str(Show.query.get(2).start_time)
  }, {
    "venue_id": venue3.id,
    "venue_name": venue3.name,
    "artist_id": artist6.id,
    "artist_name": artist6.name,
    "artist_image_link": artist6.image_link,
    "start_time": str(Show.query.get(3).start_time)
  }, {
    "venue_id": venue3.id,
    "venue_name": venue3.name,
    "artist_id": artist6.id,
    "artist_name": artist6.name,
    "artist_image_link": artist6.image_link,
    "start_time": str(Show.query.get(4).start_time)
  }, {
    "venue_id": venue3.id,
    "venue_name": venue3.name,
    "artist_id": artist6.id,
    "artist_name": artist6.name,
    "artist_image_link": artist6.image_link,
    "start_time": str(Show.query.get(5).start_time)
  }]
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
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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