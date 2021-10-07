import os
import configparser

from configparser import ConfigParser
from optparse import OptionParser

config = ConfigParser()
parser = OptionParser()

parser.add_option("-d", "--dataset",
                    help="Name of the available datasets")
parser.add_option("--tr", "--train_rate", dest="train_rate", type=float, default=1,
                  help="Part of the dataset that you want to train")
parser.add_option("-s", "--save_path",
                    help="Path to save the trained model")
parser.add_option("-m", "--model_name",
                    help="Select the backbone for training. Available backbones include: 'resnet', 'resnet50', 'alexnet', 'vgg', 'squeezenet', 'densenet', 'inception'")
parser.add_option("--fuse", default='concat',
                  help="Choose fusion methods. Available options include: 'concat', 'coatt', 'crossatt'", dest="fusion_type")
parser.add_option("-b", "--batch_size", type=int, default=32,
                    help="Batch size for training")
parser.add_option("-e", "--epochs", type=int, default=100,
                    help="the number of epochs for training")
parser.add_option("-i", "--input_size", type=int, default=224,
                  help="resize the input image")
parser.add_option("--wc", "--weighted_classes", dest="weighted_classes",
                    default=False, action='store_true',
                    help="enable if you want to train with classes weighting")
parser.add_option("--ws", "--weighted_samples", dest="weighted_samples",
                    default=False, action='store_true',
                    help="enable if you want to weight samples within batch")
parser.add_option("--lr", "--learning_rate", dest="learning_rate", type=float, default=0.01,
                    help="Learning rate")
parser.add_option("--wd", "--weights_decay", dest="weights_decay", type=float, default=0,
                    help="Weights decay")
parser.add_option("--opt", "--optimizer", dest="optimizer", type=str,
                    help="Choose optimizer: sgd, adam")
parser.add_option("--crt", "--criterion", dest="criterion", type=str, default="ce",
                  help="Choose criterion: ce, bce")
parser.add_option("--aug_type", dest="augmentation_type", type=str,
                  default="torch", help="Choose augmentation type. Available augmentation types include: torch, albumentations")
parser.add_option("--train_uct", "--train_uncertainty", dest="train_uncertainty", type=float,
                  default=0.0, help="Choose uncertainty thresholds to train without input features")
parser.add_option("--test_uct", "--test_uncertainty", dest="test_uncertainty", type=float,
                  default=0.0, help="Choose uncertainty thresholds to test without input features")
parser.add_option("--missed_feats_num", dest="missed_feats_num", type=int,
                  default=0, help="Choose the number of missed clinical features")
parser.add_option("--missing_feats_fill", dest="missing_feats_fill", type=str,
                  default='zeroes', help='Fill missing clinical feats with zeroes or by empirical sampling')
parser.add_option("--njobs", dest="num_workers", type=int,
                  default=0)

# Three-stages training hyperparams
## 1st stage
parser.add_option("--first_stage_lr",
                  dest="first_stage_learning_rate", type=float, default=0.001)
parser.add_option("--first_stage_wd",
                  dest="first_stage_weight_decay", type=float, default=0.01)
parser.add_option("--first_stage_freeze",
                  dest="first_stage_last_frozen_layer", type=int, default=158)
## 2nd stage
parser.add_option("--second_stage_lr",
                  dest="second_stage_learning_rate", type=float, default=0.0001)
parser.add_option("--second_stage_wd",
                  dest="second_stage_weight_decay", type=float, default=0.01)
parser.add_option("--second_stage_freeze",
                  dest="second_stage_last_frozen_layer", type=int, default=87)
## 3rd stage
parser.add_option("--third_stage_lr",
                  dest="third_stage_learning_rate", type=float, default=0.00001)
parser.add_option("--third_stage_wd",
                  dest="third_stage_weight_decay", type=float, default=0.01)
parser.add_option("--third_stage_freeze",
                  dest="third_stage_last_frozen_layer", type=int, default=-1)
## 4th stage
parser.add_option("--is_fourth_stage", "--is_fourth_stage", dest="train_with_fourth_stage",
                    default=False, action='store_true',
                    help="enable if you want to train with 4th stage")
parser.add_option("--fourth_stage_lr",
                  dest="fourth_stage_learning_rate", type=float, default=0.000001)
parser.add_option("--fourth_stage_wd",
                  dest="fourth_stage_weight_decay", type=float, default=0.01)
parser.add_option("--fourth_stage_freeze",
                  dest="fourth_stage_last_frozen_layer", type=int, default=-1)

# Dilated Convolution
parser.add_option("--rnet_dil_2nd",
                  dest="resnet_dilated_layer2",
                  default=False, action='store_true',
                  help="enable if you want to dilate layer2 in the torchvision resnet model")
parser.add_option("--rnet_dil_3rd",
                  dest="resnet_dilated_layer3",
                  default=False, action='store_true',
                  help="enable if you want to dilate layer3 in the torchvision resnet model")
parser.add_option("--rnet_dil_4th",
                  dest="resnet_dilated_layer4",
                  default=False, action='store_true',
                  help="enable if you want to dilate layer4 in the torchvision resnet models")

## For Test with predicted features
parser.add_option("--use_predicted_feats", dest="use_predicted_feats",
                  default=False, action='store_true',
                  help="enable if you want to use predicted clinical features for prediction")

parser.add_option("--pred_mass_shape", dest="pred_mass_shape",
                  type=str, help="Path to the prediction of mass shape of the test set")
parser.add_option("--pred_mass_margins", dest="pred_mass_margins",
                  type=str, help="Path to the prediction of mass margins of the test set")
parser.add_option("--pred_mass_density_image", dest="pred_mass_density_image",
                  type=str, help="Path to the prediction of mass density image of the test set")

parser.add_option("--pred_calc_type", dest="pred_calc_type",
                  type=str, help="Path to the prediction of calc type of the test set")
parser.add_option("--pred_calc_dist", dest="pred_calc_dist",
                  type=str, help="Path to the prediction of calc dist of the test set")
parser.add_option("--pred_calc_density_image", dest="pred_calc_density_image",
                  type=str, help="Path to the prediction of calc density image of the test set")




options, _ = parser.parse_args()
config['hyperparams'] = {}
for opt in vars(options):
    attr = getattr(options, opt)
    print(opt, attr, type(attr))

    config['hyperparams'][opt] = str(attr)

# os.makedirs(options.save_path, exist_ok=True)
# with open(os.path.join(options.save_path, 'config.ini'), 'w') as configfile:
#     config.write(configfile)


def read_config(config_path):
    print(f'{config_path} exists?', os.path.exists(config_path))
    saved_config = ConfigParser(allow_no_value=True)

    saved_config.read(config_path)

    
    for opt in vars(options):
        attr = getattr(options, opt)
        keep_default = False

        try:
            if type(attr) is int:
                saved_attr = saved_config.getint('hyperparams', opt)
            elif type(attr) is float:
                saved_attr = saved_config.getfloat('hyperparams', opt)
            elif type(attr) is bool:
                saved_attr = saved_config.getboolean('hyperparams', opt)
            else:
                saved_attr = saved_config.get('hyperparams', opt)
        except ValueError: # For in the case when of the hyperparam 'learning_rate'
            saved_attr = None
        except configparser.NoOptionError:
            # For handling when saved options file
            # do not have some fields
            keep_default = True
            
        # print(type(attr), type(saved_attr))

        if keep_default is False:
            if type(saved_attr) is type(None):
                setattr(options, opt, None)
            else:
                setattr(options, opt, saved_attr)


    return options


if __name__ == '__main__':
    print('MAIN')
    saved_options = read_config(config_path='/home/hqvo2/Projects/Breast_Cancer/experiments/cbis_ddsm/four_classes_mass_calc_pathology/with_addtional_features_r50_b32_e100_224x224_adam_wc_ws_Mon May  3 06:08:38 CDT 2021/config.ini')
    for opt in vars(saved_options):
        attr = getattr(saved_options, opt)
        print(opt, attr, type(attr))
