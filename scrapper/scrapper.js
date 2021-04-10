var querystring = require('querystring');
var https = require('https');
var cheerio = require('cheerio');
var cheerioTableparser = require('cheerio-tableparser');

var request = require('request');
var zlib = require('zlib');
const fs = require('fs')
const readline = require('readline');


getWords = (category) => {
    let f = (resolve, reject) => {
        request('https://www.wheeloffortunecheats.com/' + category, {encoding: null}, (err, response, body) => {
        if(response.headers['content-encoding'] == 'gzip'){
            zlib.gunzip(body, (err, dezipped) => {
                return resolve(dezipped.toString());
            })
        } else {
            return resolve(body);
        }
        })
    }
    return new Promise(f);
}
// getCategories = (category) => {
//   let f = (resolve, reject) => {
//     https.get('https://www.wheeloffortunecheats.com/' + category, function(res) {
//         console.log(res);
//         // let $ = cheerio.load(res.body);
//         // cheerioTableparser($);
//         // var category = $('#div').html();
//         // console.log(res);
//         res.on('data', (d) => {
//             process.stdout.write(d);
//         });
//     })
//     .on('error', function(e) {
//       console.log("Got error: " + e.message);
//       reject(e);
//     });
//     }
//   return new Promise(f);
// }

async function main() {
    const data = fs.readFileSync('categories.txt', 'utf8');
    const readInterface = readline.createInterface({
        input: fs.createReadStream('categories.txt'),
    });
    readInterface.on('line', async function(line) {
        let tokens = line.split(' ');
        let url = tokens[0];
        let name = tokens.slice(1).join(' ')
        let words = await getWords(url);
        let $ = cheerio.load(words);
        $('strong').toArray().map((m) => {
            fs.writeFileSync('data/' + name + ".txt", m.children[0].data + '\n', { flag: 'a+' }, err => {})
        });
    });

    // let words = await getWords('aroundthehouse');
    // let $ = cheerio.load(words);
    // // cheerioTableparser($);
    // // console.log(words);
    // $('strong').toArray().map((m) => console.log(m.children[0].data));
}

(async () => {
    try {
        await main();
    } catch (e) {
        // Deal with the fact the chain failed
        console.log('error', e);
    }
})();