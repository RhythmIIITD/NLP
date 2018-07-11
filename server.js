const express = require('express');
const app = express();
const request = require('request');
const cheerio = require('cheerio');
const _ = require('lodash');
var fs = require('fs');
var isUrl = require('is-url');

app.listen(3000, function () {
  console.log('NLP app listening on port 3000!')
})

app.use(express.static(__dirname + '/views'));
app.set('view engine', 'ejs');

var bodyParser = require('body-parser');
app.use(bodyParser.urlencoded({
  extended: true
}));

var multer = require('multer');

var PythonShell = require('python-shell');

//this function generated xml from wikipedia url link
function generateXml(url, callback) {
  request(url, function (err, data) {
    if (err) {
      console.log('Error while fetching wiki article');
      callback(err);
    } else {
      const $ = cheerio.load(data.body);
      var allPara = $('#bodyContent #mw-content-text .mw-parser-output > p').text();
      allPara = allPara.replace('e.g.', 'eg');
      console.log(allPara)
      allPara = allPara.replace(/\[.{1,5}\]/g,'');
      console.log(allPara)
     
      allPara = allPara.split('.');
      var xmlGenerated = '';
      xmlGenerated += '<paragraph>';
      _.forEach(allPara, function (string) {
        if (string != '') {
          xmlGenerated += '<text>';
          xmlGenerated += string;
          xmlGenerated += '</text>';
        }
      })
      xmlGenerated += '</paragraph>';
      fs.writeFile('xmlFiles/xmlFromWiki.xml', xmlGenerated, function (err, succes) {});
      callback(null, xmlGenerated);
    }
  });
}

app.get('/', function (req, res) {
  res.render('index');
});

app.post('/postUrl', function (req, res) {
  var url = req.body.url;
  if (isUrl(url) && url.toLowerCase().indexOf('wikipedia') > 0) {
    generateXml(url, function (err, xmldata) {
      var pyshell = new PythonShell('python_code.py');
      pyshell.send('1');
      // end the input stream and allow the process to exit
      pyshell.end(function (error) {
        if (error) {
          res.send({
            'statusCode': 400,
            'msg': 'Error Occured' + error
          });
        };
      });

      pyshell.on('message', function (success) {
        fs.readFile('xmlFiles/questionsGenerated.txt', 'utf8', function (error, questions) {
          // received a message sent from the Python script (a simple "print" statement)
          if (err) {
            res.send({
              'statusCode': 400,
              'msg': 'Error Occured' + err
            });
          } else {
            res.send({
              'statusCode': 200,
              'xmldata': xmldata,
              'questions': questions
            });
          }
        })
      });
    })
  } else {
    res.send({
      'statusCode': 400,
      'msg': 'Please provide valid wikipedia url'
    });
  }
})


var storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, 'xmlFiles/')
  },
  filename: function (req, file, cb) {
    cb(null, 'xmlFromFile.xml')
  }
})

var upload = multer({
  storage: storage
}).single('fileInput');

app.post('/postFile', function (req, res) {
  upload(req, res, function (err) {
    if (err) {
      res.send({
        'statusCode': 400,
        'msg': 'Error Occured' + err
      });
    } else {
      fs.readFile('xmlFiles/xmlFromFile.xml', "utf8", function (err, content) {
        var pyshell = new PythonShell('python_code.py');

        pyshell.send('2');
        // end the input stream and allow the process to exit
        pyshell.end(function (error) {
          if (error) {
            res.send({
              'statusCode': 400,
              'msg': 'Error Occured' + error
            });
          }
        });

        pyshell.on('message', function (questions) {
          fs.readFile('xmlFiles/questionsGenerated.txt', 'utf8', function (error, questions) {
            // received a message sent from the Python script (a simple "print" statement)
            if (err) {
              res.send({
                'statusCode': 400,
                'msg': 'Error Occured' + err
              });
            } else {
              res.send({
                'statusCode': 200,
                'xmldata': content,
                'questions': questions
              });
            }
          })
        });
      })
    }
  });
});
