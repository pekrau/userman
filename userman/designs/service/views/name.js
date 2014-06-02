/* Userman
   Index service documents by name.
   Value: null.
*/
function(doc) {
    if (doc.userman_doctype !== 'service') return;
    emit(doc.name, null);
}
