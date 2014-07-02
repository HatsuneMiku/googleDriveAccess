/*
  https://calendar.google.com/

  *** Must change 'calendarId' before execute this program. ***

  ( This file includes UTF-8 string for test decode/encode json string. )
*/

var calendarId = 'YOUR_ACCOUNT@gmail.com';

function createCalendarEvent() {
  var cal = CalendarApp.getCalendarById(calendarId);
  var title = 'All Calendars';
  var start = new Date();
  var end = new Date(start.getTime() + 3600 * 1000);
  var desc = '';
  var cals = CalendarApp.getAllCalendars();
  for(var i = 0; i < cals.length; ++i) desc += cals[i].getName() + ': ' + cals[i].getId() + '\n';
  var loc = '京都御所';
  var event = cal.createEvent(title, start, end, {description: desc, location: loc});
}