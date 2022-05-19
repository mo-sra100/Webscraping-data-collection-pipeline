Project-3-data-collection-pipeline

An implementation of an industry grade data collection pipeline that runs scalably in the cloud. The data collection pipeline consists of a web-scraper that collects data for products found at https://www.ebay.co.uk/sch/i.html?_from=R40&_trksid=p2047675.m570.l1313&_nkw=Shark+Anti+Hair+Wrap+Cordless+Pet+Vacuum+Cleaner&_sacat=0 using selenium. Data is stored locally as well as on AWS RDS and AWS S3. The scraper is also containerised using docker and run on an EC2 instance. Prometheus and Grafana are used to monitor the metrics. A CI/CD pipeline is then set up for this repository so that the most updated web-scraper Docker image is automatically deployed to Docker Hub every time there is a new push via the main branch.

Milestone 1:

The first step was to choose a website and build a scraper class with methods that navigate through the website including accepting cookies. This was done using xpaths found on the website. The links to different products in the item container were acquired and then stored in a list.

Milestone 2:

The next step was to make the web-scraper open each of these links and acquire the relevant information required to populate the dictionary (product ID, product name, product price, product URL, image URLs) - UUID4 labels were also generated for each item and appended to the dictionary. For each instance of running the web-scraper, a new directory was created within a folder called "raw_data" - these directories were named using the date and time at which they were made. Within these folders, the dictionary was dumped in a data.json file and the product images were downloaded and stored locally (named using their product ID).

Milestone 3:

Unit testing methods were also created and checked for the scraper to make sure it was more robust. This was done using pythons's unittest module. The unit tests include: confirming the cookies have been accepted; confirming the dictionary actually contains information and is not empty; checking the RDS does not contain duplicates using a SQL query and Numpy. Docstrings were added to explain the code.

Milestone 4:

Code was added so that the dictionary and image data was uploaded to AWS S3 using boto3; and also to upload the dictionary to RDS which can be queried using pgAdmin.

Milestone 5:

Code was refactored and adjusted to ensure it runs smoothly. Code was also added so that the web-scraper does not re-scrape any products already stored in RDS. This was done using a SQL query implemented in python that checks that the items product ID is not already within the database. Hence the structure of the code became: collect URLS for all links on the page, open each link, collect the product ID (called UID in my code) and compare this to the database – if this does not exist in the database then continue scraping all information for this product, otherwise skip it.

Milestone 6:

Options were added so that selenium can run in headless mode without issues. A docker image was made for the scraper and then containerised – this was then run on an AWS EC2 instance.

Milestone 7:

A Prometheus container was then set up to monitor the scraper including hardware metrics. This was done by configuring the daemon file for Docker as well as the prometheus.yml file to monitor the metrics of the container in the ec2 instance. A Grafana dashboard of the Prometheus metrics was also made so that the metrics can be seen more clearly.

Milestone 8:

GitHub secrets that contain my Docker Hub details were then added. This was done so that GitHub action will build the Docker image and push it to my Docker Hub account every time there is a new push to the main branch of the repository. Cronjobs were also added to the EC2 instance which pull the newest version of the web-scraper once a month (as my AWS EC2 instance has limited usage) from my Docker Hub account and run it.

The images in order below represent:
1. UML diagram
2. Locally running web-scraper and resulting AWS RDS database
3. Locally running web-scraper and resulting AWS S3 data lake
4. EC2 running web-scraper and resulting AWS RDS database
5. Targets monitored by Prometheus
6. Graphs representing container states in both Prometheus and Grafana
7. Pushing to Github and automated workflow run
8. Workflow completion and resulting Docker Hub push
9. Cronjob which instructs EC2 instance to run latest version of web-scraper on the 20th of every month at 00:45
![1-UML-diagram](https://user-images.githubusercontent.com/97900542/169419494-0c3ab631-505f-46c9-b69c-76db33c6ff7c.png)
![2-running-locally-RDS](https://user-images.githubusercontent.com/97900542/169419508-eacea046-b48e-45bf-9b85-41076e26e65d.png)
![3-running-locally-S3](https://user-images.githubusercontent.com/97900542/169419518-a7de32aa-9c29-41d1-b5bd-4a6d70f02788.png)
![4-running-EC2](https://user-images.githubusercontent.com/97900542/169419530-1d3caf38-e8f4-4dce-b2bd-65d5a1d606d4.png)
![5-PROMETHEUS-targets](https://user-images.githubusercontent.com/97900542/169419531-20ea1a2f-b87f-46fb-9ba1-e721d41e7f5c.png)
![6-PROMETHEUS-GRAFANA](https://user-images.githubusercontent.com/97900542/169419532-f834cbeb-5bd8-4734-83f4-5d89ccf93253.png)
![7-GIT-WORKFLOW](https://user-images.githubusercontent.com/97900542/169419533-74ba4012-96b2-4656-b7c1-cbd862a228b5.png)
![8-WORKFLOW-TO-DOCKERHUB](https://user-images.githubusercontent.com/97900542/169419534-64b2d617-8241-48a5-9003-c086d70c32f6.png)
![9-CRONJOBS](https://user-images.githubusercontent.com/97900542/169420652-6f0aaf3c-4a1e-4ffb-be08-e24be8507825.png)
