# URL_Shortener
Web application that creates shortened urls. Backend works using Flask. Allows options for setting a custom short url, an expiry date, and a password. Uses redis cache to make redirecting more efficient, uses Threads to make click logging asynchronous, and applies rate limiting to prevent the service from being overloaded.</br>
API routes are /api/urls, /api/urls/<short_code>, /api/analytics/last-day, /api/analytics/referrers
https://66nihaal44.github.io/URL_Shortener/
