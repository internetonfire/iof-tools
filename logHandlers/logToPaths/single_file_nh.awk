NR==1 {
		print "ASN|DEST|FROM|PATH";
}
{
		dst=$1;
		from=$2;
		path=$4;
}
{
		gsub(" from: ","",from);
		gsub(" as_path: ", "", path);
		gsub("\|", ",", path);
}
{
		print asn "|" dst "|" from "|" path;
}
