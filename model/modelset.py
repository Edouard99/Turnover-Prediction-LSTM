import torch
from model import lstm
from dataset import predset
from utils import utils
import tqdm

class ModelSet:
    """
    Models set used for prediction.
    The weights of the model are stored in /model/models_weights/

    Custom Methods:
        initialize():Creates a dictionnary of the models to use for each departement. Each model is initialized with trained weights.
        predict():Makes prediction on a predset set.
    Attributes:
        -models_dic(dic): dictionnary that contains trained models for each department.
        -models_w_dic(dic): dictionnary that contains weights of the trained models for each department.
        -initialized(bool): True if the predset has been initialized with initialize()
        -device(torch.device): device on which the models will run 
    
    """
    def __init__(self):
        self.models_dic={
                        73:None,
                        88:None,
                        117:None,
                        127:None
                        }
        self.models_w_dic={
                        73:torch.load("./model/models_weights/weights_73.pth",map_location=torch.device('cpu'))['model_state_dict'],
                        88:torch.load("./model/models_weights/weights_88.pth",map_location=torch.device('cpu'))['model_state_dict'],
                        117:torch.load("./model/models_weights/weights_117.pth",map_location=torch.device('cpu'))['model_state_dict'],
                        127:torch.load("./model/models_weights/weights_127.pth",map_location=torch.device('cpu'))['model_state_dict']
                        }
        self.initialized=False
    def initialize(self,device):
        """
        Creates a dictionnary of the models to use for each departement. Each model is initialized with trained weights.
        Args:
            -device(torch.device): device on which the models will run 
        
        """
        self.device=device
        deps=[73,88,117,127]
        for dep in deps:
            temp_model=lstm.LSTM_Turnover(False,hidden_size=64,num_of_layer=4).to(device)
            temp_model.load_state_dict(self.models_w_dic[dep])
            temp_model.eval()
            self.models_dic[dep]=temp_model
        self.initialized=True

    def predict(self,pred_set:predset.PredSet):
        """
        Makes prediction on a predset set and save the predictions in the predset set.
        Args:
            -pred_set(predset.PredSet): a set containing all the preprocessed data to make predictions.       
        
        """
        dataset_to_nn=pred_set.dataset_to_nn
        print("Starting Prediction ... \n")
        for sample in tqdm.tqdm(dataset_to_nn.samples):
            dep=sample["dep"]
            pred=self.models_dic[dep](sample["normed_x"].float().unsqueeze(0).to(self.device),
                    sample["annual_x"].float().unsqueeze(0).to(self.device),
                    sample["annual_y"].float().unsqueeze(0).to(self.device),
                    8)[0][-8:]
            pred=pred.detach().cpu().numpy()
            sample["normed_pred"]=pred
            sample["pred"]=utils.inversenorm(pred,sample["max_turn"],sample["min_turn"])
        print("Prediction complete ! \n")
