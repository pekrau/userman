/* Userman
   Index user documents by teams.
   Value: email.
*/
function(doc) {
    if (doc.userman_doctype !== 'user') return;
    for (var i in doc.teams) {
	emit(doc.teams[i], doc.email);
    }
}
