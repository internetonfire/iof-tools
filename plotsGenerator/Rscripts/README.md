## Rplot scripts

Those scripts are made for the interpretation of the CSVs produced by the logToCSV python scripts

### Main scripts
The main scripts are those used to produce the boxplot used by the fabrikant result presentation
this script is in MultipleCSV and take as input the 4 main strategies of MRAI, in the following order:
* NoMRAI
* Fix30Sec
* Fabrikant
* DPC

The second script is for the Elmokashfi experimentation, it take as input only the CSVs for the 30 second
and DPC strategy

you can use for example the following script:

`Rscript multipleCSVreader_elmokashfi.R "../../../30SEC_CSV/" "../../../DPC_CSV/"`

On the other hand is possible to print just one CSV calling the single CSV script and
passing as argument the single CSV file.