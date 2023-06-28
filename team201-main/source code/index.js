const express = require('express');
const bodyParser = require("body-parser");
const ejs = require('ejs');
const app = express();
app.set('view engine', 'ejs');
app.use(bodyParser.urlencoded({extended:true}));
app.use(express.static("public"));
const mysql = require('mysql');
var md5 = require('md5'); //for password encryption
const session = require('express-session');
const { request } = require('express');
const res = require('express/lib/response');
const { render } = require('express/lib/response');
require('dotenv').config()
const von = require("@vonage/server-sdk");
const req = require('express/lib/request');

//mysql connection
const db = mysql.createConnection({
    host: "127.0.0.1",
    user: "root",
    password: "password",
    database: "myhealth"
  });
  db.connect(function(err) {
    if (err) throw err;
    console.log("Connected!");
  });
  //tell express that we are going to use cookie sessions for when user logs in
  app.use(session({
	secret: 'secret',
	resave: true,
	saveUninitialized: true
}));
const errorMsg = "<h1>Bad entry, please try again!</h1>";




//Class for storing methods for acquiring the date when a new entry is made.
class RightNow {
    //Return the month
    static getMonth(){
        let newDate = new Date();
        return(newDate.getMonth()+1);
    }

    //Return the day
    static getDay(){
        let newDate = new Date();
        return(newDate.getDate());
    }

    //Return the hour
    static getHour(){
        let newDate = new Date();
        return(newDate.getHours());
    }

    //Return the minute
    static getMinute(){
        let newDate = new Date();
        return(newDate.getMinutes());
    }

    //get the full amount of seconds from the beginning of the year given a table
    static getFullSeconds(table){
        let seconds = 0;
        seconds += table[3]*60;
        seconds += table[2]*(60*60);
        seconds += table[1]*((60*60)*24);
        seconds += table[1]*(((60*60)*24)*30);
        return(seconds);
    }

    //above from right now
    static getFullSecondsNow(){
        return(this.getFullSeconds([this.getMonth(), this.getDay(), this.getHour(), this.getMinute()]));
    }

    //get the difference of seconds from now and given table
    static getFullSecondsFromDate(date){
        let now = this.getFullSecondsNow();
        let then = this.getFullSeconds(date);
        return(now-then);
    }
}



/*
USER BACK END
*/
//Send the login form
app.get("/", (req, res) => {
    res.render("login.ejs");
})



/*
USER BACK END
*/
//Every time someone logs in, this is called to authenticate them.
app.post("/auth", (req, res) => {
    let id = req.body.id;
    let password = md5(req.body.password); //hash the given password so it is in align with our database
    if(id && password){ //If both values exist
        db.query('SELECT * FROM users WHERE id = ? AND password = ?', [id, password], (error, results) => {
            if(error){
                throw error;
            }else {
                if(results.length > 0) { //if the database returns us something, that means that combination of password and id exists.
                        if(results[0].id == 1){ //check if the admin is logging in
                            req.session.loggedin = true;
                            req.session.username = id;
                            res.redirect("/admin");
                        }else { //if not admin, then start a normal session
                            req.session.loggedin = true;
                            req.session.username = id;
                            req.session.realname = results[0].name
                            res.redirect("/checksick");
                        }
                } else{
                    res.send(errorMsg);
                }
                res.end();
            }
        });
    } else {
        res.send("<h1>Bad entry, please try again!</h1>");
        res.end()
    }
})




/*
USER BACK END
*/
//After the user gets authenticated, they get redirected here so that they can recieve the next page.
app.get("/checksick", (req, res) => {
    if(req.session.loggedin){
        db.query("SELECT name FROM users WHERE id=?", req.session.username, (error, results) => {
            res.render("check", {username: results[0].name}); //Send the next page with the username of their account in it (retrieved from SQL database)
        });

    }else {
        res.send(errorMsg); //prompt the user to log in if they havent
    }
})
//Once the user submits if he is sick or not, we arrive here and we route the user based on their input. If they are sick then they get sent to the next page to evaluate.
app.post("/checksick", (req, res) => {
    if(req.session.loggedin){
        if(req.body.yesButton){
            res.redirect("/newsickness"); //Redirect them to the next page if they are sick
        }else if(req.body.noButton){
            let username = req.session.realname;
            res.render("mhealth");

        }
    } else {
        res.send(errorMsg);
    }
})


// 
//  USER BACK END INTERMISSION
// 
// 



//Code to give VONAGE API our keys. (STORED IN A .env FILE)
a = [process.env.KEY1, process.env.KEY2];
const vonage = new von({
    apiKey: a[0],
    apiSecret: a[1]
});

//Connecting to API to send a message
function message(number, text){
    vonage.message.sendSms(
        "18334297736",
        `1${number}`,
        text,
        (err, responseData) => {
            if (err) {
                console.log(err);
            } else {
                if (responseData.messages[0]["status"] === "0") {
                    console.dir(responseData);
                } 
            }
        }
    );
}

//This is called from the app.post("/newAlert") and also from updateTimes() which is the function that automatically sends out alerts based on certain criteria. 
function alert(disease) {
    msg = `[MYHEALTH] CAUTION - HIGH AMOUNT OF REPORTS FOR ${disease} ON SDSU CAMPUS. PLEASE PROCEED WITH CAUTION AND PRACTICE SOCIAL DISTANCING.`;

    //add alert to database
    db.query(`INSERT INTO alerts VALUES(0, "${disease}", '{"date":[${[RightNow.getMonth(), RightNow.getDay(), RightNow.getHour(), RightNow.getMinute()]}]}')`, (err, res2) => {
        if(err){
            throw err;
        }
    });

    //alert everyone in database that has a number
    db.query("SELECT number FROM users WHERE number IS NOT NULL", (err, res) => {
        if(err){
            throw err;
        } else {
            for(v in res){
                message(res[v].number, msg);
            }
        }
    }); //Retrieve all numbers from database and send message to it + put in a new entry in the alerts database.
    return(1);
}


//Algorithim to check if we need to automatically alert - called everytime the database is updated. This is neither User Back-end or Admin Back-end. This is solely to automate our code so that an admin is not really necessary. In this code, if we get 4 or more entries within the next 3 hours that have not already been used for another alert, then we will send out a new alert.
function updateTimes(){
    var timeTable = [];
    db.query("SELECT * FROM logs ORDER BY id DESC LIMIT 500", (err, res) => {
        if(err) {
            throw err;
        } else {
            for (v in res){ //Get ALL recent entries that have not been contributed to an alert already
                tempDate = JSON.parse(res[v].date).date
                if((RightNow.getFullSecondsFromDate(tempDate)/(60*60) < 3) && res[v].autoAlerted==false){
                    timeTable.push([res[v].disease, res[v].id]);
                }
            }
            let diseaseCount = new Int8Array(16); //array to hold count of each kind of disease in the past three hours
            for(v in timeTable){ //loop to count the amount of each of the recent diseases
                diseaseCount[timeTable[v][0]-1] += 1; //timeTable[v][0] is the index of the disease, so we add 1 to the field of the corresponding disease

            }
            let alertedDiseases = []
            for(v in diseaseCount){ //loop to find which diseases will be alerted based on certain criteria
                if(diseaseCount[v] >= 4 && v != 2 && v != 3 && v != 8 && v != 15){ //exclude these diseases from being automatically alerted since they are not contagious
                    alertedDiseases.push(v); //add to the list of diseases that will be alerted
                }
            }

            for(v in alertedDiseases){//do once for each disease that will be alerted
                let dis = parseInt(alertedDiseases[v]);
                //db.query("UPDATE logs SET autoAlerted = true WHERE id = 12 OR id=13")
                let updatedIDS = [];
                for(a in timeTable){ //check which entries from timeTable are in-lign with the disease
                    if(timeTable[a][0] == dis+1){
                        updatedIDS.push(timeTable[a][1]) //add their id to the list of ids that will be updated
                    }
                }
                let all = 'UPDATE logs SET autoAlerted = true WHERE';
                for(v in updatedIDS){ //Generate the SQL Query by adding all the id's we are updating to set autoAlerted to true 
                    if(v == 0){
                        all += ` id=${updatedIDS[v]}`;
                    }else {
                        all += ` OR id=${updatedIDS[v]}`;
                    }
                }
                db.query(all, (err, results) => {
                    if(err){
                        throw err;
                    } else{
                        console.log(results);
                    }
                });
                alert(diseaseNames[dis].toUpperCase());
            }
            
        }
    });
}


// 
//  END USER BACK END INTERMISSION
// 
// 



/*
USER BACK END
*/
//This is where sick people are redirected to; they get sent a page where they can choose their sickness.
app.get("/newsickness", (req, res) => {
    if(req.session.loggedin){
        res.render("disease");
    } else {
        res.send(errorMsg);
    }
})
//This is the function that is called when the user submits what sickness they have.
app.post("/newsickness", (req, res) => {
    if(req.session.loggedin){
        db.query(`INSERT INTO logs VALUES(0, ${req.session.username}, ${req.body.disease}, '{"date":[${[RightNow.getMonth(), RightNow.getDay(), RightNow.getHour(), RightNow.getMinute()]}]}', 0)`, (err, result) => { //Query to database to insert user + sickness they have, and record the date it was submitted.
            if(err){
                throw err;
            } else {
                let username = req.session.realname;
                res.render("thanks", {endMessage: `Thank you, ${username}, we hope you get better soon!`})
            }
        });
        updateTimes();
    }else {
        res.send(errorMsg);
    }
})

app.get("/page5", (req,res) => {
    if(req.session.loggedin){
        res.render("give", {name: req.session.realname});
    }
});
/*
end USER BACK END
*/
// 
// 
// 
// 
// 
// 
// 
// 
// 
// 
// 
// 
// 
// 
// 
// 
// 
// 
// 
// 
//
/*
ADMIN BACK END 
*/
//Submitting new Alerts









//Blueprint to convert date JSON from database into a human readable string value. Used for admin panel when viewing user entries and alert logs.
function convDate(d){
    let newDate = "";
    let mins = "";
    if(d.date[3] < 10){
          mins = "0" + d.date[3];
    } else {
        mins = '' + d.date[3];
    }
    if(d.date[2] < 12) {
        newDate =`(${d.date[0]}/${d.date[1]} at ${d.date[2]}:${mins} AM)`
    } else if (d.date[2] == 12){
        newDate =`(${d.date[0]}/${d.date[1]} at ${d.date[2]}:${mins} PM)`
    }else if (d.date[2] > 12) {
        let fixedHour = d.date[2]-12;
        newDate =`(${d.date[0]}/${d.date[1]} at ${fixedHour}:${mins} PM)`
    }
    return(newDate);
}











//when admin is logged in send him the admin panel
app.get("/admin", (req,res) => {
    if (req.session.loggedin && req.session.username == 1){
        res.render("admin");
    }else {
        res.send(errorMsg);
    }
})



var diseaseNames = ["COVID-19", "Cold", "Orthopedic Injury", "Unirary Tract Infection", "Food Poisoning", "Stomach Virus", "Flu", "Bronchitis", "Concussion", "Mono", "Chlamydia", "Pneumonia", "Shingles", "Chicken Pox", "Gonorrhea", "Other"];
//when admin wants to go to the next page from panel, this is called. All 3 buttons are routed through here!
app.post("/admindata", (req, res) => {
    if(req.session.loggedin && req.session.username == 1){
        if(req.body.a){
            var arr = [];
            db.query("SELECT l.id, l.user_id, l.disease, l.date, u.name FROM logs l LEFT JOIN users u ON u.id = l.user_id ORDER BY l.id DESC LIMIT 50", (err, results) => {
                if(err){
                    throw err;
                } else {
                    
                    for (v in results){ //for loop to construct array of entries with each entry stored in a master array. 
                        //temp array that will be added to master array
                        let a = []
                        a.push('' + results[v].id);
                        a.push('' +results[v].user_id);
                        a.push(diseaseNames[results[v].disease-1]);
                        a.push(results[v].name);

                        //convert the stored date into human readable form
                        a.push(convDate(JSON.parse(results[v].date)));
                        arr.push(a); //add this entry to the master array
                    }//end for loop
                } //end of sql query 
                    res.render("entries", {arr: arr}); //send out the new page generated
            })
        }else if (req.body.b){ 
            res.redirect("/getalerts"); //redirect to /getAlerts if they press the recent alerts button and continue from there.
        } else if(req.body.c){ //admin chooses to construct a new alert
            res.render("alert.ejs");
        }
    }else {
        res.send(errorMsg);
    }
})







app.post("/newAlert", (req, res) => { //First come here when admin submits new alert, checks if admin is authenticated then proceeds.
    if(req.session.loggedin && req.session.username == 1){
        alert(diseaseNames[req.body.disease-1].toUpperCase());
        res.redirect("/admin");
    } else {
        res.send(errorMsg);
    }
})




app.get("/getalerts", (req, res) => {
    db.query("SELECT * from alerts ORDER BY id DESC LIMIT 50;", (err, results) => {
        if (err) {
            throw err;
        } else {
            for(v in results){
                //console.log(results[v].date);
                results[v].date = convDate(JSON.parse(results[v].date));
            }
            //convert the dates in results


            
            res.render("alerts", {arr: results});
        }
    })
})







/*
ADMIN BACK END 
*/















app.listen(3000, () => {
    console.log('listening on port ' + 3000);
  })