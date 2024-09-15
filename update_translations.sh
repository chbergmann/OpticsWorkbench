for f in $(ls translations/*.ts); do
    pylupdate5 *.py examples/*.py -ts $f
done