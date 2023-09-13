# LinkChecker for Alma E-Portfolio / E-Collections

This script extracts HTTP-Urls stored and managed in Ex-Libris Alma E-Portfolio or E-Collections. 

* Create an *.env File
 * Add your Alma API-Key and the Collection-ID to the env-File
* Run the script
 * Script check if the stored HTTP-URls are available. 
 * If Url is available (200) a snapshot in the wayback machine is one
 * If Url is not available the script trys to get an Wayback-Archive-Url
 * The script produces a \*.xlsx-file containing all rotten links with their wayback-urls.
