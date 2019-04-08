/*
A KBase module: GenericsIndexer
*/

module GenericsIndexer {
    typedef structure {
        string file_name;
        UnspecifiedObject index;
    } Results;

    funcdef attributemapping_index(mapping<string,UnspecifiedObject> params) returns (Results output) authentication required;

    funcdef kbasematrices_index(mapping<string,UnspecifiedObject> params) returns (Results output) authentication required;

};
