/* Userman
   Index public service documents by name.
   Value: null.
*/
function(doc) {
    if (doc.userman_doctype !== 'service') return;
    if (!doc.public) return;
    emit(doc.name, null);
}
