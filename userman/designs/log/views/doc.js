/* Userman
   Index log documents by doc.
   Value: timestamp.
*/
function(doc) {
    if (doc.userman_doctype !== 'log') return;
    emit(doc.doc, doc.timestamp);
}
