# from Logger import mainLogger



from OpenAnalytics.LoggerOA.AppLoggersOA import main_logger 
import OpenAnalytics.ENV

main_logger.debug("Hola Mundo")
main_logger.error("Este es un error")
main_logger.warning("este es un warning")
main_logger.critical("Este es critical")
main_logger.info("Este es un info")