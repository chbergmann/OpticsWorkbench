for f in translations/*_*.ts
do
    lrelease "$f"
done
