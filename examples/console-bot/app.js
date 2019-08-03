//var app = require('http').createServer(response);
var connect = require("connect");
const express = require('express');
var cors = require('cors');
const app = express();
var fs = require('fs');
var bodyParser = require('body-parser')
app.use(bodyParser.json()); // to support JSON-encoded bodies
app.use(bodyParser.urlencoded({ // to support URL-encoded bodies
    extended: true
}));
app.use(express.json()); // to support JSON-encoded bodies
app.use(express.urlencoded()); // to support URL-encoded bodies
app.use(cors())
app.listen(3000);
console.log("App running...");

const { NlpManager } = require('../../lib');
const { NerManager } = require('node-nlp');
const trainnlp = require('./train-nlp');
const entitiesnlp = require('./entities-nlp');

const EntityManager = new NerManager({ threshold: 0.95 });
const threshold = 0.5;
const nlpManager = new NlpManager({ languages: ['en'] });

function say(message) {
    // eslint-disable-next-line no-console
    console.log(message);
}

app.get('/', function(req, res) {
    res.send('Hello World')
})

app.post('/conversation', (req, res) => {
    res.setHeader('Content-Type', 'application/json');
    var line = req.body.text;
    console.log("User==> " + line);
    var obj = new Object();

    (async() => {
        await trainnlp(nlpManager, say);
        await entitiesnlp(EntityManager, say);
        try {
            const result = await nlpManager.process(line);
            const answer =
                result.score > threshold && result.answer ?
                result.answer.charAt(0).toUpperCase() + result.answer.slice(1) :
                "Sorry, I can understand you";
            let sentiment = '';
            if (result.sentiment.score !== 0) {
                sentiment = `  ${result.sentiment.score > 0 ? ':)' : ':('}   (${
							result.sentiment.score
							})`;
            }
            say(`bot> ${answer}${sentiment}`);
            obj.answer = answer;

            var useEntities = false;
            var arrEntities = [];
            var arrEntitiesInfo = [];
                EntityManager.findEntities(
                    line,
                ).then(entities => {
                    try {
                        for (var i = 0; i < entities.length; i++) {
                            if (entities[i].entity != "number" & entities[i].entity != "percentage" & entities[i].entity != "boolean" &
                                entities[i].entity != "currency") {
                                var descripcionEntidad = "***** Entity: " + entities[i].entity + " ***** Option: " + entities[i].option + ", Sub-element: " + entities[i].sourceText + " ,Accuracy: " + entities[i].accuracy;
                                console.log(descripcionEntidad);
                                arrEntities.push(descripcionEntidad);
                            }
                        }
                    } catch (err) {

                    }
                    var jsonString = JSON.stringify(obj);
                    res.send("User: " + line + "\n" + jsonString);
                });
            }
        catch (err) {
            say('Invalid entry. Ask again ')
        }

    })();
});