import $ from 'jquery';
import { Modal } from 'bootstrap';

let gbifSearchString = '';
let rr = document.getElementById('gbif-list');
let tabContent = document.getElementById('gbif-nav-tabContent');
let speciesLookup = new Map();

let id_name = document.getElementById('id_name')
let id_gbif_key = document.getElementById('id_gbif_key')
let id_gbif_canonical_name = document.getElementById('id_gbif_canonical_name')
let id_gbif_class = document.getElementById('id_gbif_class')
let id_gbif_order = document.getElementById('id_gbif_order')
let id_gbif_family = document.getElementById('id_gbif_family')
let id_gbif_genus = document.getElementById('id_gbif_genus')
let id_gbif_species = document.getElementById('id_gbif_species')
let id_gbif_scientific_name = document.getElementById('id_gbif_scientific_name')
let id_gbif_status = document.getElementById('id_gbif_status')
let id_gbif_rank = document.getElementById('id_gbif_rank')

let messageModalBody = document.getElementById('messageModal-body');
let messageModal = new Modal(document.getElementById('messageModal'), {
    keyboard: false
  })

function getListHtml(row) {
  return `<a class="list-group-item list-group-item-action" id="${row.key}" data-bs-toggle="list" href="#list-${row.key}"
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
      speciesLookup.set(String(row.key), row);
     }
  })
})
.done(function() {
  //console.log(speciesLookup.get(0)) // will use a .get from map to obtain selected values to save to db
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
  if (!gbifSearchString) {
    messageModalBody.innerHTML = 'Please enter a search string.';
    messageModal.show();
  } else {
    getGbif(gbifSearchString);
  }
})

searchInput.addEventListener('keypress', function(event) {
  if (event.key === 'Enter') {
    event.preventDefault();
    $searchButton.trigger('click');
  }
});


let $selectGbifButton = $('<button class="btn btn-success btn-sm mb-1 text-nowrap" type="button">Use Selected GBIF</button>')
$('.select-gbif-button').append($selectGbifButton)
$selectGbifButton.on('click', function(event) {

  let gbif_selected = document.getElementsByClassName('list-group-item list-group-item-action active');

  if (gbif_selected.length) {
  let v = speciesLookup.get(gbif_selected[0].id)
  id_name.value = v.canonicalName;
  id_gbif_key.value = v.key;
  id_gbif_canonical_name.value = v.canonicalName;
  if (v.class) { id_gbif_class.value = v.class; };
  if (v.order) { id_gbif_order.value = v.order; };
  if (v.family) { id_gbif_family.value = v.family; };
  if (v.genus) { id_gbif_genus.value = v.genus; };
  if (v.species) { id_gbif_species.value = v.species; };
  id_gbif_scientific_name.value = v.scientificName;
  id_gbif_status.value = v.taxonomicStatus;
  id_gbif_rank.value = v.rank;

  } else {
    messageModalBody.innerHTML = `First, Search for a taxon, Then select one of the listed taxa below,
    then use this button to choose your final selection`;
    messageModal.show();
  }
})

});
