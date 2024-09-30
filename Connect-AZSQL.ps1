function Connect-AZSQL {                                                                                                                                           
	param($ConnectionString)
	
	while ($true) {
		$sqlconn = [System.Data.SqlClient.SqlConnection]::new($ConnectionString)
		$sqlconn.Open()

		$cmd = [System.Data.SqlClient.SqlCommand]::new()
		# Exclude semi-colon terminator (;) at the end of your queries
    $cmd.Connection = $sqlconn
	
		$query = (Read-Host -Prompt "Query >")
		$cmd.CommandText = $query
		$reader = $cmd.ExecuteReader()

		while ($reader.Read()) {
			$reader.GetValue(0)
		}
	}
    
    $sqlconn.Close()
}
