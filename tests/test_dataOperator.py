import pytest

import lidarSuit as lst


def test_dataOperator_dbsOperations_fileList_none():
    
    with pytest.raises(FileNotFoundError):
    
        lst.dbsOperations(fileList=None, varList=['range'])
        
def test_dataOperator_dbsOperations_varList_none():
    
    with pytest.raises(KeyError):
    
        lst.dbsOperations(fileList=['file_path'], varList=None)
