import libs.NLP as NLP


class TestNLPTokensMethods: 

    def setup_method(self): 

        self.tokens = NLP.Tokens()

        


    def test_num_tokens_from_string(self): 
        print(self.sql_manager.__dict__)
        assert self.sql_manager is not None 

    def test_create_embeddings(self):
        pass


    def test_process_text(self):
        pass


class TestNLPHyperDBMethods: 

    def setup_method(self): 

        self.HyperDB = NLP.HyperDB()


    def test_num_tokens_from_string(self): 
        print(self.sql_manager.__dict__)
        assert self.sql_manager is not None 

    def test_create_embeddings(self):
        pass


    def test_process_text(self):
        pass



class TestChatBotHandlerMethods():
    pass
