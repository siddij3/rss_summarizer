#TODO

def test_addition(): 
  assert 1 + 1 == 2 


class TestStringMethods: 

  def setup_method(self): 
    self.text = "hello world" 

  def test_upper(self): 
    assert self.text.upper() == "HELLO WORLD" 

  def test_lower(self): 
    assert self.text.lower() == "hello world" 