# -*- coding: utf-8 -*-
import re, os, time, sys
import requests
from datetime import datetime

# general configs
if (len(sys.argv) > 1):
	max_price = sys.argv[1]
else:
	max_price = input("Set a price (Euro):\n")

print("Price set to: ",str(max_price)," €")

time_start = time.time()
spitogatos_website_timeout = 280
output_html = "private_listings.html"

spitogatos_homepage = "https://spitogatos.gr"
spitogatos_nof_listings_in_page = 10
spitogatos_total_listings_pattern = r'searchTotalNumberOfResults">[^<]+<b>(\d+[\.]*\d*)<'

spitogatos_url = spitogatos_homepage + "/search/results/residential/sale/r100/m100m101m102m103m104m/order_datemodified_desc"
spitogatos_url += "/uploaded_month" # only listings added last month
spitogatos_url += "/floorNumber_ground_floor-nd" #  # >= Ground Floor
spitogatos_url += "/price_nd-"+str(max_price)
spitogatos_url += "/offset_0" # start from page 1

xe_homepage = "https://www.xe.gr"
xe_total_listings_pattern = r'r_subtitle">[^>]+>(\d*[\.]*\d*)<'
xe_page_pattern = r'r_paging_label">[^>]+>(\d*)[^>]+>[^>]+>(\d*)'
xe_url = xe_homepage + "/property/search?"

xe_url_param = {
"Geo.area_id_new__hierarchy":"82196", "Publication.age":"10", "Publication.by_agent":"0", "System.item_type":"re_residence",
"Transaction.price.to":str(max_price), "Transaction.type_channel":"117518", "per_page":"50", "sort_by":"Publication.effective_date_start","sort_direction":"desc",
"Publication.level_num.from":"1", # >= Ground Floor"page":"1"}
"page":"1"}


def request_url(url, params=""):
	headers = {
    'Accept':'*/*',
    'Accept-Encoding':'gzip, deflate, br, sdch',
    'Connection':'keep-alive',
	'User-agent':'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.16 Safari/537.36', 'Content-Type': 'text/javascript; charset=utf-8'}

	cookies = dict(cookies_are='working')

	response = requests.get(url, params=params, cookies=cookies, headers=headers, allow_redirects="False")
	# print(response.url)

	if (int(response.status_code) == 200):
		content = response.text
	else:
		print("\nhttp Error with Code:",response.status_code)
		content = ""

	return content


def checkTimeout(time_start, website_timeout):
	if ((int(time.time())-int(time_start)) > website_timeout):
		print("wait 10s to avoid connection error\n")
		time.sleep(10)
		return True
	else:
		return False


def update_progress(item_id, total_items):
	if (float(total_items) != 0.0):
		progress = 100*(int(item_id)/float(total_items))
	else:
		progress = 0
	sys.stdout.write('\r[{0}] {1}%'.format('#'*int(progress/10), int(progress)))
	sys.stdout.flush()

def find_total_listings(page, listings_in_page_pattern):
	# page = request_url(page_link)
	total_listings = re.search(listings_in_page_pattern, page)
	if total_listings:
		return(total_listings.group(1).replace(".",""))
	else:
		print("Not able to find total listings number. Exiting...\n")
		exit(1)


def find_current_total_pages(page, page_pattern):
	match_page = re.compile(page_pattern).findall(page)
	return(match_page[0])


spitogatos_listings_html_body = ""
search_timeout = int(time.time())


page_count = 0
total_listings = 0
found_listings = 0

print("\nSearching in Spitogatos.gr\n")
while(spitogatos_url):
	if checkTimeout(search_timeout, spitogatos_website_timeout):
		search_timeout = time.time()

	url = request_url(spitogatos_url)

	all_listings_match = re.compile(r'searchListing_title"><a href="([^"]+".{1,2800})sg\-icon\-private', re.DOTALL).findall(url)
	if all_listings_match:
		for listing in all_listings_match:
			match = re.compile(r'([^"]+)".+?</h4>[^<]+<div[^>]+>([^<]+)</div>[^<]*<div[^>]+>[^<]+<strong[^>]+>(\d{1,2}\/\d{1,2}\/\d{4})[^>]+>([^<]+)<.+?class="listingPrice">[^>]+>([^<]+)\D+(\d+)', re.DOTALL).findall(listing)
			if match:
				for link, region, date, desc, price, size in match:
					found_listings += 1
					listing_link = link
					spitogatos_listings_html_body += "<a target=\"_blank\" href="+listing_link+"><b>"+price+"</b>  "+size+"m2  ("+date+")  "+region+"  "+desc+"</a><br>\n"

	next_page = re.findall(r'<link rel="next" href="([^"]+)"',url)
	if not next_page:
		spitogatos_url = ""
		break
	else:
		spitogatos_url = next_page[0]
		page_count += 1

	total_listings = find_total_listings(url, spitogatos_total_listings_pattern)
	if (spitogatos_nof_listings_in_page != 0):
		update_progress(page_count,(float(int(total_listings)/spitogatos_nof_listings_in_page)))

print("\nSpitogatos completed. "+str(found_listings)+" listings of total",str(total_listings),"found.\n")


# xe.gr
print("\nSearching in Xe.gr.\n")

xe_website_pause = 1800

xe_links_list = []
xe_listings_html_body = ""

total_listings = 0
total_listing_pages = 0
found_listings = 0
page_count = 1

print("\nSearching in Xe.gr.\n")

while(xe_url):
	url = request_url(xe_url, xe_url_param)

	if (url):
		all_listings_match = re.compile(r'class="lazy[\S|\s]+?<ul class=\"r_actions[\S\s]+?</ul>[\S\s]{1,300}</div').findall(url)
		# print(all_listings_match[1])
		for listing in all_listings_match:
			private_listings_match = re.compile(r'r_desc[^<]+<h2>\s*<a href="([^"]+)"[\S\s]+?<p>([^<]+)[\S\s]+?r_stats">([\S\s]+?)<li>(\d+)[\S\s]+?r_date">([\S\s]+?)</p>[\S\s]+?</ul>[\s]{1,20}</div').findall(listing)
			if private_listings_match:
				# print("match")
				for link, desc, price_field, size, date in private_listings_match:
					found_listings += 1
					# check if price is given
					price_match = re.findall(r'r_price">([\S\s]+)<',price_field)
					if price_match:
						price = price_match[0]
					else:
						price = "xx.xxx €"
					date = date.rstrip()
					xe_listings_html_body += "<a target=\"_blank\" href=\""+xe_homepage+link+"\"><b>"+price+"</b>  "+size+"m2  ("+date+")  "+ desc+"</a><br>\n"
			# 	else:
			# 		print("No match")
			# else:
			# 	print("no match at all")


		page_id, total_listing_pages = find_current_total_pages(url, xe_page_pattern)
		page_count = int(page_id)
		update_progress(page_count, total_listing_pages)
		page_count += 1

	else:
		print("\nRetry in",xe_website_pause,"s again")
		time.sleep(xe_website_pause)


	if (page_count > int(total_listing_pages)):
		# print("\nlast page")
		total_listings = find_total_listings(url, xe_total_listings_pattern)
		break
	else:
		# update next page
		xe_url_param["page"] = str(page_count)


print("\nXE.gr completed. "+str(found_listings)+" listings of total",str(total_listings),"found.\n")



# write links to an html file
raw_file = '<HTML>\n<HEAD>\n<meta charset="utf-8">\n<TITLE>Αγγελίες Κατοικιών μόνο από Ιδιώτες</TITLE></HEAD>\n<BODY BGCOLOR="FFFFFF">\n'
raw_file += '<H2>Λίστα με ακίνητα τελευταίου μήνα <b>μόνο από ιδιώτες</b> και τιμή μέχρι '+str(max_price)+' € (' + str(datetime.today().strftime("%Y-%m-%d, %H:%M")) + ')</H1>\n'

raw_file += '<div><a href="https://en.spitogatos.gr/"><img src="https://cdn.spitogatos.gr/frontend/images/logo/logo.header.new.en.png"></a></div>\n'
raw_file += spitogatos_listings_html_body

raw_file += '<br>\n<div><a href="https://www.xe.gr/property/"><img src="https://static.xe.gr/property/images/property_logo_new.png"></a></div>\n'
raw_file += xe_listings_html_body

raw_file += "</BODY></HTML>"


f = open(output_html, 'w', encoding="utf-8")
f.write(raw_file)
f.close

print("\nProgram completed sucessfully in " + '{:.0f}'.format(time.time() - time_start) +" seconds\n")
