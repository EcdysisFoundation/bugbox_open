import $ from 'jquery';

let gbifSearchString = '';
let rr = document.getElementById('gbif-results-rows');
let speciesLookup = new Map();

function getRowHtml(row) {
  let result = '<div class="row">';
  let valuesArray = [row.rank, row.order, row.family, row.genus, row.canonicalName]
  for (let i in valuesArray) {
    result += '<div class="col">' + valuesArray[i] + '</div>';
  }
  result += '</div>'; // close row div
  return result
}


function getGbif( param ) { $.get( 'https://api.gbif.org/v1/species/search', {
  datasetKey: 'd7dddbf4-2cf0-4f39-9b2a-bb099caae36c',
  q: param,
  isExtinct: false,
  limit: 40,
}, function( data ) {

  document.getElementById('gbif-results-rows').innerHTML = ""
  speciesLookup.clear()
  data.results.forEach(function (row, index) {
     if (row.phylum == 'Arthropoda' && row.rank != 'SUBSPECIES') {
      rr.innerHTML += getRowHtml(row)
      speciesLookup.set(index, row)
     }
  })
})
.done(function() {
  console.log(speciesLookup.get(0))
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
