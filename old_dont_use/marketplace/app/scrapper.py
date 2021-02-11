import urllib.request
from bs4 import BeautifulSoup


def getCareerBlissJobs():
    sock = urllib.request.urlopen("https://www.careerbliss.com/search/?q=Healthcare%20Assistant&l=&typeFilter=job&sf=true")
    htmlSource = sock.read()                            
    sock.close()  
    output = []
    soup = BeautifulSoup(htmlSource)  
    nextli = True
    while nextli:
        jobs = soup.find(id='bodyContainer').find("div").find("div").find_all("div")[2].find_all("div")[2].find_all("div")[1].find("div")
        print(jobs)
        return "Cant access data"

def getZippiaJobs():
    sock = urllib.request.urlopen("https://www.zippia.com/arizona-city-az-jobs/")
    htmlSource = sock.read()                            
    sock.close()
    soup = BeautifulSoup(htmlSource)
    output = []
    jobs = soup.find("zp-card-proxy")
    print(jobs)
    return "nothing found"

def getJobxoomJobs():
    sock = urllib.request.urlopen("http://www.jobxoom.com/jobfind.php?action=search&auth_sess=llpvl5oprgnsimc38ugp3mbjk3&ref=34eb2b5cddb8fecdaaa06c6c9&kwd=hea&city=&jids%5B%5D=83#.XiHKicj7Q2w")
    htmlSource = sock.read()                            
    sock.close()
    soup = BeautifulSoup(htmlSource)
    jobs = soup.find(id='idjobsearchresults').find_all("div")
    output = []
    nexturl = True
    while nexturl:
        for job in jobs:
            try:
                clas = job["class"]
                if "results" in clas:
                    h = job.find("a", href=True)["href"]
                    j = job.find("a").getText().replace("\n", "").replace("\t", "")
                    k = job.find_all("p", attrs={"class":"desc"})[-1].getText().replace("Employer/Recuiter:","").strip().replace("\n", "").replace("\t", "")
                    desc = job.find("p", attrs={"class":"desc1"}).getText().replace("\n", "").replace("\t", "")
                    logo = ""
                    try:
                        state = k.split(" - ")[1]
                        city = k.split(" - ")[2]
                        country = k.split(" - ")[3]
                        k = k.split(" - ")[0].replace("\n", "").replace("\t", "")
                    except:
                        state = ""
                        city = ""
                        country = ""
                        k = ""
                    start = job.find("span", attrs={"class":"posted"}).getText().replace("Posted on: ", "").replace("\n", "").replace("\t", "")
                    end = ""
                    output.append({"link":h, "name":j, "organization":k, "desc":desc, "logo":logo, "country":country, "state":state, "city":city, "start":start, "end":end})
            except Exception as e:
                print(e)
                continue
        nexturl = soup.find_all("li", attrs={"class":"nolist"})[-1].find("a", href=True)["href"]
        try:
            sock = urllib.request.urlopen(nexturl)
            htmlSource = sock.read()                            
            sock.close()
            soup = BeautifulSoup(htmlSource)
            jobs = soup.find(id='idjobsearchresults').find_all("div")
        except:
            nexturl = None
    return output


def getJobvertiseJobs():
    sock = urllib.request.urlopen("http://www.jobvertise.com/jobs/search?query=care&city=&radius=30&state=AZ&button=Search+Jobs")
    htmlSource = sock.read()                            
    sock.close()
    soup = BeautifulSoup(htmlSource)
    output = []
    try:
        jobs = soup.find("body").find_all("center")[15].find("table").find_all("table")
    except:
        jobs = soup.find("body").find_all("center")[16].find("table").find_all("table")
    for job in jobs:
        try:
            j = job.find("span").getText()
            h = job.find("a", href=True)["href"]
            k1 = job.find_all("tr")[0].find_all("span")[2]
            k1 = str(k1).split("<br/>")
            desc = ""
            logo = ""
            state = k1[0].split(" ")[-1]
            city = k1[0].split(" ")[-2].strip(",").split(">")[-1]
            k = ""
            if "Company Name:" not in k1[1]:
                desc = k1[1]
            else:
                desc = "Position"+k[1].split("Position")[1]
                k = k1[1].split("Position")[0].replace("Company Name:", "")
            country = "US"
            start = k1[-1].split("<")[0]
            end = ""
            print(h)
            output.append({"link":h, "name":j, "organization":k, "desc":desc, "logo":logo, "country":country, "state":state, "city":city, "start":start, "end":end})
        except Exception as e:
            print(e)
            continue
    return output
