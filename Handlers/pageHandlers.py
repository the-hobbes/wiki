'''
	Contains all the handlers for various functions, such as rendering pages, logging in and out, as well as sigining up. 
	Also has more exotic methods for wiki page editing.
'''
from common import *

class MainHandler(Handler):
	'''
		main page renderer
	'''
	def get(self):
		# self.write('Hello world!')
		self.render("main.html")

class EditPage(Handler):
	'''
		when you want to edit a wiki page
	'''
	def get(self, page):
		self.write('edit page accessed')

	def post(self):
		pass

class WikiPage(Handler):
	'''
		when you want to view a wiki page
	'''
	def get(self, page):
		self.write('WikiPage accessed')
		# must check the database for the presence of the page, and if it doesn't exist redirect to /_edit/page

	def post(self):
		pass

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
				self.redirect("/welcome")

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
			self.redirect('/welcome')
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