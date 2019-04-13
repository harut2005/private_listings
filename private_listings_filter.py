# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, time, io
from datetime import datetime

# general configs
price = input("Set a price (Euro):\n")
# price = 78000 # 3



time_start = time.time()
spitogatos_website_timeout = 280
output_html = "private_listings.html"

spitogatos_url = "https://spitogatos.gr/search/results/residential/sale/r100/m100m101m102m103m104m/order_datemodified_desc"
spitogatos_url += "/uploaded_month"
spitogatos_url += "/price_nd-"+str(price)
spitogatos_url += "/offset_0"#+str(offset)

xe_url = "https://www.xe.gr/property/search?Geo.area_id_new__hierarchy=82196&System.item_type=re_residence&Transaction.price.to="+str(price)+"&Transaction.type_channel=117518&per_page=50&sort_by=Publication.effective_date_start&sort_direction=desc&page=2&Publication.age=30"



def checkTimeout(time_start, website_timeout):
	if ((int(time.time())-int(time_start)) > website_timeout):
		print "wait 10s to avoid connection error\n"
		time.sleep(10)
		return True
	else:
		return False

spitogatos_listings_html_body = ""
# spitogatos_links_list = []
search_timeout = int(time.time())
count = 0

print "\nSpitogatos started.\n"
while(spitogatos_url):
	if checkTimeout(search_timeout, spitogatos_website_timeout):
		search_timeout = time.time()
	
	# print spitogatos_url.rsplit("offset_")[0]
	print "Searching in page "+str(1+int(spitogatos_url.rsplit("offset_")[1])/10)
	response = urllib2.urlopen(spitogatos_url)
	url = response.read()
	response.close()



	# match = re.compile(r'media.{1,50}.gr/([^"]+").{1,2800}sg\-icon sg\-icon\-private', re.DOTALL).findall(url)
	# if match:
	# 	for link in match:
	# 		count += 1
	# 		listing_link = link
	# 		# print date+price+desc+filt
	# 		print listing_link
	# 		# spitogatos_links_list.append(listing_link)
	# 		spitogatos_listings_html_body += "<a target=\"_blank\" href="+listing_link+">"+listing_link+"</a><br>\n"


	# match = re.compile(r'h4 class="text color cyan larger  semibold searchListing_title"><a href="([^"]+)".+?</h4>[^<]+<div[^>]+>([^<]+)</div>[^<]*<div[^>]+>[^<]+<strong[^>]+>(\d{1,2}\/\d{1,2}\/\d{4})[^>]+>([^<]+)<.+?class="listingPrice">[^>]+>([^<]+)\D+(\d+)', re.DOTALL).findall(url))
	# match = re.compile(r'searchListing_title"><a href="([^"]+)">[^<]+<[^<]+</span></a></h4>[^<]+<div[^>]+>([^<]+)</div>[^<]*<div[^>]+>[^<]+<strong[^>]+>(\d{1,2}\/\d{1,2}\/\d{4})[^>]+>([^<]+)</div>\s*</div>\s*</div>.+?<div class="listingPrice">[^>]+>([^<]+)\D+(\d+)(.{1,800}private)', re.DOTALL).findall(url) #listingIcons)
	

	all_listings_match = re.compile(r'searchListing_title"><a href="([^"]+".{1,2800})sg\-icon\-private', re.DOTALL).findall(url)
	if all_listings_match:
		for listing in all_listings_match:
			match = re.compile(r'([^"]+)".+?</h4>[^<]+<div[^>]+>([^<]+)</div>[^<]*<div[^>]+>[^<]+<strong[^>]+>(\d{1,2}\/\d{1,2}\/\d{4})[^>]+>([^<]+)<.+?class="listingPrice">[^>]+>([^<]+)\D+(\d+)', re.DOTALL).findall(listing)
			if match:
				for link, region, date, desc, price, size in match:
					count += 1
					listing_link = link
					# print date+price+desc+filt
					print listing_link
					# spitogatos_links_list.append(listing_link)
					spitogatos_listings_html_body += "<a target=\"_blank\" href="+listing_link+"><b>"+price+"</b>  "+size+"m2  ("+date+")  "+region+"  "+desc+"</a><br>\n"	

	next_page = re.findall(r'<link rel="next" href="([^"]+)"',url)
	# print next_page
	if not next_page:
		spitogatos_url = ""
		break
	else:
		spitogatos_url = next_page[0]

print "\nSpitogatos completed. "+str(count)+" listings found.\n"



# xe.gr

xe_website_timeout = 1800
search_timeout = int(time.time())
xe_links_list = []
xe_listings_html_body = ""
count = 0

print "\nxe.gr started.\n"
while(xe_url):
	if checkTimeout(search_timeout, xe_website_timeout):
		search_timeout = time.time()

	page_match = re.search(r"&page=(\d+)&Pub", xe_url)
	if page_match:
		print "Searching in page " + str(page_match.group(1))
	# req = urllib2.Request(xe_url)
	# response = urllib2.urlopen(req)
	response = urllib2.urlopen(xe_url)
	url = response.read()
	response.close()


	match = re.compile(r'<div class="lazy[^<]+<a href="([^"]+)".+?</a><br>([^<]+)</p>.+?<li class="r_price">([^<]+).+?<p class="r_date">([^<]+).+?</ul>[^<]+</div>', re.DOTALL).findall(url)
	if match:
		for link, desc, price, date in match:
			count += 1
			xe_listings_html_body += "<a target=\"_blank\" href="+link+"><b>"+price +"</b>  ("+date+")  "+ desc+"</a><br>\n"
			print link


	next_page = re.findall(r'<td>[^<]+<a href="([^"]+)" class="white_button right+',url)
	# print next_page
	if not next_page:
		xe_url = ""
		break
	else:
		xe_url = next_page[0]
	# print xe_url

	print "\nXE.gr completed. "+str(count)+" listings found.\n"





# write links to an html file
#<CENTER><IMG SRC="clouds.jpg" ALIGN="BOTTOM"> </CENTER>
raw_file = '<HTML>\n<HEAD>\n<meta charset="utf-8">\n<TITLE>Spitogatos</TITLE></HEAD>\n<BODY BGCOLOR="FFFFFF">\n'
raw_file += '<H2>Λίστα με ακίνητα <b>μόνο από ιδιώτες</b> και τιμή μέχρι '+price+' + ' (' + str(datetime.today().strftime("%Y-%m-%d")) + ')</H1>\n'
# raw_file += '<input type="button" id=\'script\' name="scriptbutton" value=" Ανανέωση " onclick="exec(\'python spitogatos.py\');window.location.reload();">\n'
raw_file += '<div><a href="https://en.spitogatos.gr/"><img src="https://cdn.spitogatos.gr/frontend/images/logo/logo.header.new.en.png"></a></div>\n'
raw_file += spitogatos_listings_html_body

raw_file += '<br>\n<div><a href="https://www.xe.gr/property/"><img src="https://static.xe.gr/property/images/property_logo_new.png"></a></div>\n'
# for listing in xe_links_list:
# 	raw_file += "<a href="+listing+">"+listing+"</a><br>\n"
raw_file += xe_listings_html_body

raw_file += "</BODY></HTML>"
# print raw_file

f = open(output_html, 'w')
f.write(raw_file)
f.close

print "\nProgram completed sucessfully in " + '{:.0f}'.format(time.time() - time_start) +" seconds\n"

