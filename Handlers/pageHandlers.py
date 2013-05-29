'''
	Contains all the handlers for various functions, such as rendering pages, logging in and out, as well as sigining up. 
	Also has more exotic methods for wiki page editing.
'''
from common import *
import Models.datastore as datastore

class MainHandler(Handler):
	'''
		main page renderer
	'''
	def get(self):
		cookieStr = self.request.cookies.get('user_id')

		if cookieStr:
			# user is logged in
			self.render("main.html", logout = "Logout |", edit = "Edit")
		else:
			# no user logged in
			self.render("main.html", loggedIn = "Login |", signup = "Signup ")


class EditPage(Handler):
	'''
		when you want to edit a wiki page
	'''
	def get(self, page):
		# check and see if the page is already in the database. if it is, get the text.
		wiki_entry = Wiki.by_title(page)
		text=""
		if wiki_entry:
			text = wiki_entry.text

		# if the user is logged in, let them edit the page
		if self.user:
			self.render('wiki.html', text=text, editable=True, page=page)
		# if the user is not logged in, then show them the page if it exists
		elif not self.user:
			self.render('wiki.html', text=text)
		# if the page doesn't exist and they aren't logged in, then direct them back to the homepage
		else:
			self.redirect('/')

	def post(self, page):
		# self.write("you posted.")
		content = str(self.request.get('content'))

		# if things don't pass validation, then spit out the error and rerender the page
		if (not content):
			error = "You need some content there, bub."
			self.render('wiki.html', text=content, editable=True, error=error, page=page)		

		# if everything passes validation, then update the datastore and render the page
		else:
			# success, interact with the datastore entity Posts, creating a new row with the right information information
			wiki_entry=Wiki.by_title(page)
			if wiki_entry:
				# update the wiki entry
				wiki_entry.text = content
				wiki_entry.put()
				time.sleep(1)
			else:
				# create a new entry
				w = Wiki(title=page, text=content)
				w.put()
				time.sleep(1)

			self.redirect(page)
		

class WikiPage(Handler):
	'''
		when you want to view a wiki page
	'''
	def get(self, page):
		# self.write('WikiPage accessed')
		# must check the database for the presence of the page
		wiki_entry = Wiki.by_title(page)
		text=""
		# if the page exists, render that page
		if wiki_entry:
			editMenu=False
			if self.user:
				editMenu=True
			text = wiki_entry.text
			self.render('wiki.html', text=text, editMenu=editMenu, page=page)
		# if the page doesn't exist, and they are logged in, direct them to the edit page
		elif (not wiki_entry and self.user):
			self.redirect('/_edit' + page)
		# if the page doesn't exist but they are not logged in, direct them to the home page
		else:
			self.redirect('/')

class Signup(Handler):
	'''
		handle users signing up
	'''
	def get(self):
		self.renderLanding()

	def renderLanding(self):
		self.render("signupForm.html")

	def post(self):
		# form validation section
		uname = str(self.request.get('username'))
		pword = str(self.request.get('password'))
		email = str(self.request.get('email'))

		have_error, params = self.validateInput(self.request)

		if have_error:
			# do this if there is an error
			self.render('signupForm.html', **params)
		else:
			# make sure the user doesn't already exist
			u = datastore.User.by_name(uname)
			if u:
				msg = "User already exists"
				self.render('signupForm.html', error_username = msg)
			else:
				u = u = User.register(uname, pword, email)
				u.put()

				self.login(u)
				self.redirect("/")

class Login(Handler):
	'''
		handle users logging in
	'''
	def get(self):
		self.render("login.html")

	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')

		# interact with datastore
		u = User.login(username, password)

		if u:
			# set secure cookie and redirect to blog
			self.login(u)
			self.redirect('/')
		else:
			msg = "Invalid Login"
			self.render("login.html", error = msg)

class Logout(Handler):
	'''
		handle users logging out
	'''
	def get(self):
		# get the login cookie user_id and set it to nothing, then redirect to the signup page

		if self.request.cookies.get('user_id'):
			self.logout()

		self.redirect("/")