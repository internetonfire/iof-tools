NR==1 {
		print "ASN|DEST|PATH";
}
{
		dst=$1;
		path=$4;
}
{
		gsub(" as_path: ", "", path);
		gsub("\|", ",", path);
}
{
		print asn "|" dst "|" path;
}
