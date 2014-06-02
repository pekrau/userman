/* Userman
   Index team documents by name.
   Value: null.
*/
function(doc) {
    if (doc.userman_doctype !== 'team') return;
    emit(doc.name, null);
}
