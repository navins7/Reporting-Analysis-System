<? php
$Name = $_POST['Name'];
$Location = $_POST['Location'];
$Email = $_POST['Email'];
$Complain = $_POST['message'];

$host= "localhost";
$dbUsername= "root";
$dbPassword= "9563";
$dbname="test1";

$conn= new mysqli($host,$dbName,$dbLocation,$dbEmail,$dbComplain);

if (mysqli_connect_error()){
	die('Connect Error('.mysqli_connect_error().')'.mysqli_connect_error());
}else {
	$SELECT= "SELECT Email From register where Email= ?Limit 1';
	$INSERT= "INSERT Into register (Name,Location,Email,message) values(?,?,?,?)";

	$stmt =$conn->prepare($SELECT);
	$stmt->bind_param("s",$Email);
	$stmt->execute();
	$stmt->maxdb_bind_result($Email);
	$stmt->store_result();
	$rnum=$stmt->num_rows;

	if ($rnum==0)
	{
		$stmt->close();

		$stmt=$conn->prepare($INSERT);
		$stmt->bind_param("hello",$Name,$Location,$Email,$message);
		$stmt->execute();
		echo "New record inserted";

	}
	$stmt->close();
	$conn->close();
}

?>
