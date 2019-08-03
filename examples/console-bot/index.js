const readline = require('readline');
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

(async() => {
    await trainnlp(nlpManager, say);
    await entitiesnlp(EntityManager, say);
    say('Say something!');
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout,
        terminal: false,
    });
    rl.on('line', async line => {
        try {
            if (line.toLowerCase() === 'quit') {
                rl.close();
                process.exit();
            } else {
                const result = await nlpManager.process(line);
                const answer =
                    result.score > threshold && result.answer ?
                    result.answer.charAt(0).toUpperCase() + result.answer.slice(1) :
                    "Sorry, I can not understand you";
                let sentiment = '';
                if (result.sentiment.score !== 0) {
                    sentiment = `  ${result.sentiment.score > 0 ? ':)' : ':('}   (${
            result.sentiment.score
            })`;
                }
                say(`bot> ${answer}${sentiment}`);
                //say(`bot> ${JSON.stringify(result.utterance)}`);
                var useEntities = false;
                if (useEntities) {
                    EntityManager.findEntities(
                        line,
                    ).then(entities => {
                        try {
                            for (var i = 0; i < entities.length; i++) {
                                if (entities[i].entity != "number" & entities[i].entity != "percentage" & entities[i].entity != "boolean" &
                                    entities[i].entity != "currency") {
                                    console.log("***** Entity: " + entities[i].entity + " ***** Option: " + entities[i].option + ", Sub-element: " + entities[i].sourceText + " ,Accuracy: " + entities[i].accuracy);
                                }
                            }
                        } catch (err) {

                        }
                    });
                }

            }
        } catch (err) {
            say('Invalid entry. Ask again ')
        }
    });
})();