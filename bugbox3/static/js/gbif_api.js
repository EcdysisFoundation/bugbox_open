import $ from 'jquery';

let gbifSearchString = '';
let rr = document.getElementById('gbif-list');
let tabContent = document.getElementById('gbif-nav-tabContent');
let speciesLookup = new Map();


function getListHtml(row) {
  return `<a class="list-group-item list-group-item-action" id="list-
  ${row.key}-list" data-bs-toggle="list" href="#list-${row.key}"
  role="tab" aria-controls="list-${row.key}">${row.canonicalName}</a>`
}

function getTabDetails(row) {
  let li = '<li class="list-group-item d-flex justify-content-between align-items-start">'
  let lic = '</li>'
  let result = `<ul class="list-group list-group-flush">
  ${li}<b>Rank:</b> ${row.rank}${lic}
  ${li}<b>Class:</b> ${row.class}${lic}
  ${li}<b>Order:</b> ${row.order}${lic}
  ${li}<b>Family:</b> ${row.family}${lic}
  ${li}<b>Genus:</b> ${row.genus}${lic}
  ${li}<b>Scientific Name:</b> ${row.scientificName}${lic}
  `;
  if (row.publishedIn) {
    result +=`${li}<b>Published In</b>${lic}
    ${li}${row.publishedIn}${lic}`;
  }
  if (row.descriptions.length) {
    result += `${li}<b>Descriptions</b>${lic}`
    for (let i in row.descriptions) {
      result += `${li}${row.descriptions[i].description}${lic}`
    }
  }
  return result
}

function getTabHTML(row) {
  return `<div class="tab-pane fade" id="list-${row.key}"
  role="tabpanel" aria-labelledby="list-${row.key}-list">
  ${getTabDetails(row)}</div>`
}

function getGbif( param ) { $.get( 'https://api.gbif.org/v1/species/search', {
  datasetKey: 'd7dddbf4-2cf0-4f39-9b2a-bb099caae36c',
  q: param,
  isExtinct: false,
  limit: 40,
}, function( data ) {

  rr.innerHTML = ""
  tabContent.innerHTML = ""
  speciesLookup.clear()

  data.results.forEach(function (row, index) {
     if (row.phylum == 'Arthropoda' && row.rank != 'SUBSPECIES') {
      rr.innerHTML += getListHtml(row);
      tabContent.innerHTML += getTabHTML(row);
      speciesLookup.set(index, row);
     }
  })
})
.done(function() {
  console.log(speciesLookup.get(0)) // will use a .get from map to obtain selected values to save to db
})
.fail(function() {
  alert( "error" );
})
.always(function() {
  //alert( "finished" );
})
}


$(function () {

let searchInput = document.getElementById('gbif-input');

let $searchButton = $('<button class="btn btn-success btn-sm mb-1 text-nowrap" type="button">Search GBIF</button>')
$('.search-button').append($searchButton)
$searchButton.on('click', function() {
  gbifSearchString = searchInput.value;
  getGbif(gbifSearchString);
})

searchInput.addEventListener('keypress', function(event) {
  if (event.key === 'Enter') {
    event.preventDefault();
    $searchButton.trigger('click');
  }
});


});
