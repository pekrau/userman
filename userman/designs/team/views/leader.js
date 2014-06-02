/* Userman
   Index team documents by leaders.
   Value: name.
*/
function(doc) {
    if (doc.userman_doctype !== 'team') return;
    for (var i in doc.leaders) {
	emit(doc.leaders[i], doc.name);
    }
}
