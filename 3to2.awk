BEGIN			{	
					class = ""
					FS = "[ \t()]+"
				}

/^class/		{
					class = $2
					print
					next
				}

/super\(\)\./	{	
					sub("super\\(\\)\\.", "super(" class ", self).", $0)
					print
					next
				}

				{
					print
				}

