"""
Populate the database with B1-C1 level vocabulary words with Vietnamese translations
Run this script to add 200+ intermediate to advanced English words
"""

from app import app, db
from models import Vocabulary
from cambridge_api import fetch_pronunciation_data
from datetime import datetime, timedelta
import random
import time

# Comprehensive vocabulary words organized by CEFR levels (B1-C1)
vocabulary_data = {
    'B1': [
        {'word': 'accomplish', 'definition': 'To succeed in doing something', 'example': 'She accomplished all her goals this year.', 'translation': 'Hoàn thành, đạt được'},
        {'word': 'advantage', 'definition': 'Something that helps you succeed', 'example': 'Speaking two languages is a great advantage.', 'translation': 'Lợi thế, ưu điểm'},
        {'word': 'approach', 'definition': 'A way of dealing with something', 'example': 'We need a different approach to solve this problem.', 'translation': 'Cách tiếp cận, phương pháp'},
        {'word': 'benefit', 'definition': 'An advantage or profit gained from something', 'example': 'The benefits of exercise are well known.', 'translation': 'Lợi ích, phúc lợi'},
        {'word': 'challenge', 'definition': 'A difficult task that tests ability', 'example': 'Learning a new language is a big challenge.', 'translation': 'Thách thức'},
        {'word': 'combine', 'definition': 'To join or mix together', 'example': 'We need to combine our efforts to succeed.', 'translation': 'Kết hợp'},
        {'word': 'contribute', 'definition': 'To give something to help achieve a result', 'example': 'Everyone should contribute to the team project.', 'translation': 'Đóng góp'},
        {'word': 'demonstrate', 'definition': 'To show clearly by giving proof', 'example': 'The teacher will demonstrate how to solve the equation.', 'translation': 'Chứng minh, trình diễn'},
        {'word': 'efficient', 'definition': 'Working well without wasting time or energy', 'example': 'This new system is more efficient than the old one.', 'translation': 'Hiệu quả'},
        {'word': 'establish', 'definition': 'To set up or create something', 'example': 'The company was established in 1990.', 'translation': 'Thành lập, thiết lập'},
        {'word': 'evaluate', 'definition': 'To judge or calculate the quality or value', 'example': 'Teachers evaluate students through various tests.', 'translation': 'Đánh giá'},
        {'word': 'expand', 'definition': 'To become or make larger', 'example': 'The company plans to expand its business overseas.', 'translation': 'Mở rộng'},
        {'word': 'maintain', 'definition': 'To keep something in good condition', 'example': 'It is important to maintain a healthy lifestyle.', 'translation': 'Duy trì'},
        {'word': 'perspective', 'definition': 'A particular way of viewing things', 'example': 'Travel gives you a new perspective on life.', 'translation': 'Quan điểm, góc nhìn'},
        {'word': 'significant', 'definition': 'Large or important enough to notice', 'example': 'There was a significant improvement in his grades.', 'translation': 'Đáng kể, quan trọng'},
        {'word': 'influence', 'definition': 'The power to affect someone or something', 'example': 'Parents have a strong influence on their children.', 'translation': 'Ảnh hưởng'},
        {'word': 'achieve', 'definition': 'To successfully complete or gain something', 'example': 'He achieved his dream of becoming a doctor.', 'translation': 'Đạt được, giành được'},
        {'word': 'analyze', 'definition': 'To examine something in detail', 'example': 'Scientists analyze data to draw conclusions.', 'translation': 'Phân tích'},
        {'word': 'convince', 'definition': 'To make someone believe something', 'example': 'She convinced me to join the program.', 'translation': 'Thuyết phục'},
        {'word': 'determine', 'definition': 'To find out or decide something', 'example': 'We need to determine the cause of the problem.', 'translation': 'Xác định, quyết định'},
        {'word': 'predict', 'definition': 'To say what will happen in the future', 'example': 'It is difficult to predict the weather accurately.', 'translation': 'Dự đoán'},
        {'word': 'require', 'definition': 'To need something', 'example': 'This job requires excellent communication skills.', 'translation': 'Yêu cầu, đòi hỏi'},
        {'word': 'emphasize', 'definition': 'To give special importance to something', 'example': 'The teacher emphasized the importance of practice.', 'translation': 'Nhấn mạnh'},
        {'word': 'resolve', 'definition': 'To find a solution to a problem', 'example': 'They resolved their differences through discussion.', 'translation': 'Giải quyết'},
        {'word': 'decline', 'definition': 'To become less or worse', 'example': 'Sales have declined over the past year.', 'translation': 'Giảm sút, từ chối'},
        {'word': 'invest', 'definition': 'To put money into something to make profit', 'example': 'Many people invest in stocks and bonds.', 'translation': 'Đầu tư'},
        {'word': 'obtain', 'definition': 'To get or acquire something', 'example': 'She obtained a degree from Harvard University.', 'translation': 'Có được, đạt được'},
        {'word': 'promote', 'definition': 'To help something develop or increase', 'example': 'Exercise promotes good health.', 'translation': 'Thúc đẩy, quảng bá'},
        {'word': 'construct', 'definition': 'To build or make something', 'example': 'They are constructing a new bridge.', 'translation': 'Xây dựng'},
        {'word': 'generate', 'definition': 'To produce or create something', 'example': 'Solar panels generate electricity from sunlight.', 'translation': 'Tạo ra, sinh ra'},
        {'word': 'consist', 'definition': 'To be made up of something', 'example': 'The team consists of ten members.', 'translation': 'Bao gồm'},
        {'word': 'involve', 'definition': 'To include or contain as a part', 'example': 'The job involves a lot of travel.', 'translation': 'Liên quan, bao gồm'},
        {'word': 'participate', 'definition': 'To take part in an activity', 'example': 'Everyone is encouraged to participate in the discussion.', 'translation': 'Tham gia'},
        {'word': 'adapt', 'definition': 'To change to suit different conditions', 'example': 'Animals adapt to their environment over time.', 'translation': 'Thích nghi'},
        {'word': 'indicate', 'definition': 'To show or point out', 'example': 'The results indicate a positive trend.', 'translation': 'Chỉ ra, cho thấy'},
        {'word': 'depend', 'definition': 'To rely on someone or something', 'example': 'Success depends on hard work.', 'translation': 'Phụ thuộc'},
        {'word': 'assume', 'definition': 'To accept something as true without proof', 'example': 'I assume you have already finished the work.', 'translation': 'Cho rằng, giả định'},
        {'word': 'implement', 'definition': 'To put a plan into action', 'example': 'The company will implement new policies next month.', 'translation': 'Thực hiện'},
        {'word': 'diverse', 'definition': 'Showing a great deal of variety', 'example': 'The city has a diverse population.', 'translation': 'Đa dạng'},
        {'word': 'consider', 'definition': 'To think carefully about something', 'example': 'Please consider my proposal carefully.', 'translation': 'Xem xét, cân nhắc'},
        {'word': 'associate', 'definition': 'To connect or link in the mind', 'example': 'I always associate this song with summer.', 'translation': 'Liên kết, kết hợp'},
        {'word': 'modify', 'definition': 'To make small changes to something', 'example': 'We need to modify our plans slightly.', 'translation': 'Sửa đổi'},
        {'word': 'interact', 'definition': 'To communicate or work together', 'example': 'Students interact with each other during group work.', 'translation': 'Tương tác'},
        {'word': 'ignore', 'definition': 'To deliberately pay no attention to', 'example': 'You cannot ignore the facts.', 'translation': 'Bỏ qua, phớt lờ'},
        {'word': 'attitude', 'definition': 'A way of thinking or feeling about something', 'example': 'She has a positive attitude toward life.', 'translation': 'Thái độ'},
        {'word': 'principle', 'definition': 'A basic truth or belief', 'example': 'He always acts according to his principles.', 'translation': 'Nguyên tắc'},
        {'word': 'context', 'definition': 'The circumstances that form the setting', 'example': 'You need to understand the context of the situation.', 'translation': 'Bối cảnh, ngữ cảnh'},
        {'word': 'function', 'definition': 'The purpose or role of something', 'example': 'The function of the heart is to pump blood.', 'translation': 'Chức năng'},
        {'word': 'sufficient', 'definition': 'Enough for a particular purpose', 'example': 'We have sufficient resources to complete the project.', 'translation': 'Đủ, đầy đủ'},
        {'word': 'initial', 'definition': 'Happening at the beginning', 'example': 'The initial results look promising.', 'translation': 'Ban đầu'},
    ],
    'B2': [
        {'word': 'acknowledge', 'definition': 'To accept or admit that something is true', 'example': 'He acknowledged that he made a mistake.', 'translation': 'Thừa nhận'},
        {'word': 'comprehensive', 'definition': 'Including everything that is necessary', 'example': 'The report provides a comprehensive analysis of the situation.', 'translation': 'Toàn diện'},
        {'word': 'deteriorate', 'definition': 'To become worse in quality or condition', 'example': 'His health began to deteriorate after the accident.', 'translation': 'Xấu đi, suy giảm'},
        {'word': 'elaborate', 'definition': 'Developed in great detail; complicated', 'example': 'She presented an elaborate plan for the new project.', 'translation': 'Chi tiết, phức tạp'},
        {'word': 'legitimate', 'definition': 'Conforming to the law or rules', 'example': 'She has a legitimate reason for being absent.', 'translation': 'Hợp pháp'},
        {'word': 'predominant', 'definition': 'Being the most important or noticeable', 'example': 'English is the predominant language in business.', 'translation': 'Chủ yếu, nổi bật'},
        {'word': 'reluctant', 'definition': 'Unwilling and hesitant', 'example': 'He was reluctant to accept the new position.', 'translation': 'Miễn cưỡng'},
        {'word': 'substantial', 'definition': 'Of considerable importance or size', 'example': 'They made a substantial investment in the company.', 'translation': 'Đáng kể'},
        {'word': 'ambiguous', 'definition': 'Open to more than one interpretation', 'example': 'His answer was ambiguous and unclear.', 'translation': 'Mơ hồ, không rõ ràng'},
        {'word': 'arbitrary', 'definition': 'Based on random choice rather than reason', 'example': 'The decision seemed arbitrary to many people.', 'translation': 'Tùy ý, chủ quan'},
        {'word': 'coherent', 'definition': 'Logical and consistent', 'example': 'She presented a coherent argument.', 'translation': 'Mạch lạc, nhất quán'},
        {'word': 'contemporary', 'definition': 'Belonging to the present time', 'example': 'Contemporary art often challenges traditional ideas.', 'translation': 'Đương đại'},
        {'word': 'enhance', 'definition': 'To improve the quality or value of something', 'example': 'Technology can enhance the learning experience.', 'translation': 'Nâng cao, tăng cường'},
        {'word': 'inevitable', 'definition': 'Certain to happen; unavoidable', 'example': 'Change is inevitable in any organization.', 'translation': 'Không thể tránh khỏi'},
        {'word': 'manipulate', 'definition': 'To control or influence cleverly', 'example': 'Some politicians manipulate public opinion.', 'translation': 'Thao túng'},
        {'word': 'profound', 'definition': 'Very great or intense', 'example': 'The book had a profound effect on her thinking.', 'translation': 'Sâu sắc'},
        {'word': 'radical', 'definition': 'Relating to fundamental change', 'example': 'The government introduced radical reforms.', 'translation': 'Triệt để, cấp tiến'},
        {'word': 'rational', 'definition': 'Based on reason and logic', 'example': 'We need to make a rational decision.', 'translation': 'Hợp lý'},
        {'word': 'sophisticated', 'definition': 'Highly developed and complex', 'example': 'The company uses sophisticated technology.', 'translation': 'Tinh vi, phức tạp'},
        {'word': 'subsequent', 'definition': 'Coming after something in time', 'example': 'Subsequent events proved him right.', 'translation': 'Tiếp theo, sau đó'},
        {'word': 'suspend', 'definition': 'To temporarily stop or delay', 'example': 'The match was suspended due to rain.', 'translation': 'Đình chỉ, hoãn lại'},
        {'word': 'undertake', 'definition': 'To commit oneself to a task', 'example': 'She undertook the responsibility of managing the project.', 'translation': 'Đảm nhận'},
        {'word': 'advocate', 'definition': 'To publicly recommend or support', 'example': 'Many experts advocate for renewable energy.', 'translation': 'Ủng hộ, vận động'},
        {'word': 'constraint', 'definition': 'A limitation or restriction', 'example': 'Budget constraints limited our options.', 'translation': 'Hạn chế, ràng buộc'},
        {'word': 'contradict', 'definition': 'To assert the opposite of a statement', 'example': 'The evidence contradicts his testimony.', 'translation': 'Mâu thuẫn'},
        {'word': 'implicit', 'definition': 'Suggested though not directly expressed', 'example': 'There was an implicit understanding between them.', 'translation': 'Ngầm hiểu'},
        {'word': 'inhibit', 'definition': 'To hinder or restrain', 'example': 'Fear can inhibit creativity.', 'translation': 'Ngăn cản, kìm hãm'},
        {'word': 'mutual', 'definition': 'Shared by two or more people', 'example': 'They have a mutual respect for each other.', 'translation': 'Lẫn nhau, tương hỗ'},
        {'word': 'parallel', 'definition': 'Similar and happening at the same time', 'example': 'There are parallel developments in both countries.', 'translation': 'Song song'},
        {'word': 'preliminary', 'definition': 'Coming before the main event', 'example': 'The preliminary results are encouraging.', 'translation': 'Sơ bộ'},
        {'word': 'conform', 'definition': 'To comply with rules or standards', 'example': 'All products must conform to safety regulations.', 'translation': 'Tuân theo'},
        {'word': 'compensate', 'definition': 'To give something to make up for loss', 'example': 'The company will compensate victims of the accident.', 'translation': 'Bồi thường'},
        {'word': 'inherent', 'definition': 'Existing as a natural part of something', 'example': 'Risk is inherent in any business venture.', 'translation': 'Vốn có, cố hữu'},
        {'word': 'integral', 'definition': 'Necessary to make something complete', 'example': 'Music is an integral part of their culture.', 'translation': 'Không thể thiếu'},
        {'word': 'prominent', 'definition': 'Important or well-known', 'example': 'She is a prominent figure in politics.', 'translation': 'Nổi bật, quan trọng'},
        {'word': 'persistent', 'definition': 'Continuing firmly despite difficulty', 'example': 'Her persistent efforts finally paid off.', 'translation': 'Kiên trì'},
        {'word': 'simulate', 'definition': 'To imitate the appearance of something', 'example': 'The program can simulate real-world conditions.', 'translation': 'Mô phỏng'},
        {'word': 'allocate', 'definition': 'To distribute resources for a purpose', 'example': 'We need to allocate more funds to education.', 'translation': 'Phân bổ'},
        {'word': 'justify', 'definition': 'To show something to be right or reasonable', 'example': 'Can you justify your decision?', 'translation': 'Biện minh'},
        {'word': 'diminish', 'definition': 'To make or become less', 'example': 'The pain will diminish over time.', 'translation': 'Giảm bớt'},
        {'word': 'accumulate', 'definition': 'To gather or acquire gradually', 'example': 'Dust accumulates quickly in empty rooms.', 'translation': 'Tích lũy'},
        {'word': 'dispose', 'definition': 'To get rid of something', 'example': 'Please dispose of waste properly.', 'translation': 'Vứt bỏ, xử lý'},
        {'word': 'expose', 'definition': 'To make something visible or known', 'example': 'The investigation exposed corruption.', 'translation': 'Phơi bày'},
        {'word': 'tolerate', 'definition': 'To allow without protest', 'example': 'I will not tolerate such behavior.', 'translation': 'Chịu đựng'},
        {'word': 'undergo', 'definition': 'To experience or be subjected to', 'example': 'The building will undergo renovations.', 'translation': 'Trải qua'},
        {'word': 'assign', 'definition': 'To allocate a task to someone', 'example': 'The teacher assigned homework to the students.', 'translation': 'Giao phó'},
        {'word': 'compile', 'definition': 'To collect and arrange information', 'example': 'We compiled a list of useful resources.', 'translation': 'Biên soạn'},
        {'word': 'deviate', 'definition': 'To depart from an established course', 'example': 'Do not deviate from the plan.', 'translation': 'Lệch khỏi'},
        {'word': 'intervene', 'definition': 'To come between to prevent or alter', 'example': 'The police had to intervene to stop the fight.', 'translation': 'Can thiệp'},
        {'word': 'revise', 'definition': 'To examine and make changes', 'example': 'I need to revise my essay before submission.', 'translation': 'Sửa đổi, ôn tập'},
    ],
    'C1': [
        {'word': 'abstract', 'definition': 'Existing in thought but not having physical form', 'example': 'Love is an abstract concept that is hard to define.', 'translation': 'Trừu tượng'},
        {'word': 'contemplate', 'definition': 'To think about something carefully', 'example': 'She contemplated her future career options.', 'translation': 'Suy ngẫm'},
        {'word': 'confer', 'definition': 'To grant or bestow something', 'example': 'The university will confer degrees next month.', 'translation': 'Ban tặng, bàn bạc'},
        {'word': 'deduce', 'definition': 'To arrive at a conclusion by reasoning', 'example': 'From the evidence, we can deduce what happened.', 'translation': 'Suy ra'},
        {'word': 'depict', 'definition': 'To represent by drawing or describing', 'example': 'The painting depicts a rural landscape.', 'translation': 'Miêu tả'},
        {'word': 'discriminate', 'definition': 'To treat differently based on prejudice', 'example': 'It is illegal to discriminate based on race.', 'translation': 'Phân biệt đối xử'},
        {'word': 'elicit', 'definition': 'To draw out a response or fact', 'example': 'The question elicited an interesting discussion.', 'translation': 'Gợi ra'},
        {'word': 'eradicate', 'definition': 'To destroy completely', 'example': 'Scientists are working to eradicate diseases.', 'translation': 'Xóa bỏ'},
        {'word': 'formulate', 'definition': 'To create or devise methodically', 'example': 'The team formulated a strategy for success.', 'translation': 'Hình thành'},
        {'word': 'fluctuate', 'definition': 'To change irregularly', 'example': 'Prices fluctuate according to supply and demand.', 'translation': 'Dao động'},
        {'word': 'illuminate', 'definition': 'To light up or clarify', 'example': 'The research illuminates many important issues.', 'translation': 'Chiếu sáng, làm sáng tỏ'},
        {'word': 'impose', 'definition': 'To force something to be accepted', 'example': 'The government imposed new taxes.', 'translation': 'Áp đặt'},
        {'word': 'incorporate', 'definition': 'To include as part of a whole', 'example': 'We need to incorporate feedback into our design.', 'translation': 'Kết hợp vào'},
        {'word': 'induce', 'definition': 'To bring about or give rise to', 'example': 'Stress can induce headaches.', 'translation': 'Gây ra'},
        {'word': 'infer', 'definition': 'To deduce from evidence', 'example': 'From her tone, I inferred that she was upset.', 'translation': 'Suy luận'},
        {'word': 'innovate', 'definition': 'To introduce new ideas or methods', 'example': 'Companies must innovate to stay competitive.', 'translation': 'Đổi mới'},
        {'word': 'intrinsic', 'definition': 'Belonging naturally; essential', 'example': 'Exercise has intrinsic value for health.', 'translation': 'Nội tại'},
        {'word': 'invoke', 'definition': 'To call on or appeal to', 'example': 'He invoked his right to remain silent.', 'translation': 'Viện dẫn'},
        {'word': 'juxtapose', 'definition': 'To place side by side for contrast', 'example': 'The article juxtaposes two opposing viewpoints.', 'translation': 'Đặt cạnh nhau'},
        {'word': 'mitigate', 'definition': 'To make less severe or serious', 'example': 'Measures were taken to mitigate the impact.', 'translation': 'Giảm nhẹ'},
        {'word': 'permeate', 'definition': 'To spread throughout', 'example': 'The smell of coffee permeated the room.', 'translation': 'Thấm qua'},
        {'word': 'perpetuate', 'definition': 'To cause to continue indefinitely', 'example': 'Such attitudes perpetuate inequality.', 'translation': 'Duy trì mãi mãi'},
        {'word': 'preclude', 'definition': 'To prevent from happening', 'example': 'His injury precluded him from playing.', 'translation': 'Ngăn cản'},
        {'word': 'proliferate', 'definition': 'To increase rapidly in number', 'example': 'Fast food restaurants have proliferated.', 'translation': 'Tăng nhanh'},
        {'word': 'reconcile', 'definition': 'To make compatible or settle a disagreement', 'example': 'They reconciled their differences.', 'translation': 'Hòa giải'},
        {'word': 'reinforce', 'definition': 'To strengthen or support', 'example': 'The experience reinforced my beliefs.', 'translation': 'Củng cố'},
        {'word': 'relinquish', 'definition': 'To give up or cease to keep', 'example': 'He was forced to relinquish control.', 'translation': 'Từ bỏ'},
        {'word': 'scrutinize', 'definition': 'To examine closely and critically', 'example': 'The committee scrutinized the proposal.', 'translation': 'Xem xét kỹ'},
        {'word': 'stipulate', 'definition': 'To demand or specify as a condition', 'example': 'The contract stipulates payment terms.', 'translation': 'Quy định'},
        {'word': 'subside', 'definition': 'To become less intense or widespread', 'example': 'The pain should subside in a few hours.', 'translation': 'Giảm dần'},
        {'word': 'supersede', 'definition': 'To replace or take the place of', 'example': 'New regulations will supersede the old ones.', 'translation': 'Thay thế'},
        {'word': 'sustain', 'definition': 'To maintain or keep going', 'example': 'We need to sustain economic growth.', 'translation': 'Duy trì'},
        {'word': 'tangible', 'definition': 'Perceptible by touch; clear and definite', 'example': 'We need tangible evidence, not just theories.', 'translation': 'Hữu hình, rõ ràng'},
        {'word': 'ubiquitous', 'definition': 'Present everywhere', 'example': 'Smartphones have become ubiquitous in society.', 'translation': 'Có mặt khắp nơi'},
        {'word': 'undermine', 'definition': 'To weaken or damage gradually', 'example': 'Such criticism can undermine confidence.', 'translation': 'Phá hoại'},
        {'word': 'unify', 'definition': 'To make or become united', 'example': 'The goal is to unify the team.', 'translation': 'Thống nhất'},
        {'word': 'validate', 'definition': 'To confirm the accuracy of', 'example': 'The results validate our hypothesis.', 'translation': 'Xác nhận'},
        {'word': 'versatile', 'definition': 'Able to adapt to many functions', 'example': 'She is a versatile actress.', 'translation': 'Linh hoạt, đa năng'},
        {'word': 'warrant', 'definition': 'To justify or necessitate', 'example': 'The situation warrants immediate action.', 'translation': 'Bảo đảm, đòi hỏi'},
        {'word': 'yield', 'definition': 'To produce or provide', 'example': 'The investment yielded good returns.', 'translation': 'Sinh ra, nhường bộ'},
        {'word': 'amplify', 'definition': 'To increase in size or strength', 'example': 'The microphone amplifies sound.', 'translation': 'Khuếch đại'},
        {'word': 'articulate', 'definition': 'To express clearly in words', 'example': 'He articulated his concerns clearly.', 'translation': 'Diễn đạt rõ ràng'},
        {'word': 'ascertain', 'definition': 'To find out for certain', 'example': 'We need to ascertain the facts.', 'translation': 'Xác định'},
        {'word': 'bolster', 'definition': 'To support or strengthen', 'example': 'The news bolstered investor confidence.', 'translation': 'Hỗ trợ'},
        {'word': 'circumvent', 'definition': 'To find a way around an obstacle', 'example': 'They tried to circumvent the rules.', 'translation': 'Vượt qua'},
        {'word': 'coerce', 'definition': 'To persuade by force or threats', 'example': 'He was coerced into signing the document.', 'translation': 'Ép buộc'},
        {'word': 'concede', 'definition': 'To admit something is true', 'example': 'He conceded that he was wrong.', 'translation': 'Thừa nhận'},
        {'word': 'consolidate', 'definition': 'To combine into a single unit', 'example': 'The company consolidated its operations.', 'translation': 'Hợp nhất'},
        {'word': 'contend', 'definition': 'To assert or compete', 'example': 'She contends that the policy is unfair.', 'translation': 'Tranh luận'},
        {'word': 'converge', 'definition': 'To come together from different directions', 'example': 'The paths converge at the summit.', 'translation': 'Hội tụ'},
        {'word': 'delineate', 'definition': 'To describe precisely', 'example': 'The report delineates the main issues.', 'translation': 'Phác thảo'},
        {'word': 'disseminate', 'definition': 'To spread widely', 'example': 'The internet helps disseminate information.', 'translation': 'Phổ biến'},
        {'word': 'embody', 'definition': 'To give tangible form to an idea', 'example': 'She embodies the spirit of innovation.', 'translation': 'Hiện thân'},
        {'word': 'engender', 'definition': 'To cause or give rise to', 'example': 'Trust engenders loyalty.', 'translation': 'Gây ra'},
        {'word': 'exacerbate', 'definition': 'To make a problem worse', 'example': 'The delay exacerbated the situation.', 'translation': 'Làm trầm trọng thêm'},
        {'word': 'exemplify', 'definition': 'To be a typical example of', 'example': 'His work exemplifies excellence.', 'translation': 'Minh họa'},
        {'word': 'facilitate', 'definition': 'To make an action easier', 'example': 'Technology facilitates communication.', 'translation': 'Tạo điều kiện'},
        {'word': 'feasible', 'definition': 'Possible and practical to achieve', 'example': 'The plan is technically feasible.', 'translation': 'Khả thi'},
        {'word': 'foster', 'definition': 'To encourage the development of', 'example': 'We need to foster creativity.', 'translation': 'Nuôi dưỡng'},
        {'word': 'impede', 'definition': 'To delay or prevent', 'example': 'Bad weather impeded our progress.', 'translation': 'Cản trở'},
        {'word': 'incentivize', 'definition': 'To motivate through rewards', 'example': 'The program incentivizes healthy behavior.', 'translation': 'Khuyến khích'},
        {'word': 'instigate', 'definition': 'To bring about or initiate', 'example': 'He instigated the reforms.', 'translation': 'Xúi giục'},
        {'word': 'manifest', 'definition': 'To display or show clearly', 'example': 'His stress manifested as headaches.', 'translation': 'Biểu hiện'},
        {'word': 'negate', 'definition': 'To nullify or make ineffective', 'example': 'One mistake can negate all your efforts.', 'translation': 'Phủ định'},
        {'word': 'pervasive', 'definition': 'Spreading widely throughout', 'example': 'There is a pervasive sense of optimism.', 'translation': 'Lan tỏa'},
        {'word': 'pragmatic', 'definition': 'Dealing with things realistically', 'example': 'We need a pragmatic approach.', 'translation': 'Thực dụng'},
        {'word': 'resilient', 'definition': 'Able to recover quickly from difficulties', 'example': 'Children are remarkably resilient.', 'translation': 'Kiên cường'},
        {'word': 'streamline', 'definition': 'To make more efficient', 'example': 'We need to streamline the process.', 'translation': 'Tinh giản'},
        {'word': 'transcend', 'definition': 'To go beyond the limits of', 'example': 'Art transcends cultural boundaries.', 'translation': 'Vượt qua'},
        {'word': 'unprecedented', 'definition': 'Never done or known before', 'example': 'We are facing unprecedented challenges.', 'translation': 'Chưa từng có'},
    ]
}

def populate_database():
    with app.app_context():
        # Ensure database tables are created
        db.create_all()
        
        # Check if database already has data
        existing_count = Vocabulary.query.count()
        if existing_count > 0:
            print(f"Database already contains {existing_count} words.")
            response = input("Do you want to add more words anyway? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("Operation cancelled.")
                return
        
        added_count = 0
        skipped_count = 0
        
        print("\nAdding B1-C1 vocabulary words with Vietnamese translations...")
        print("=" * 70)
        
        for level, words in vocabulary_data.items():
            print(f"\n{level} Level: Adding {len(words)} words...")
            
            for word_data in words:
                # Check if word already exists
                existing = Vocabulary.query.filter_by(word=word_data['word'].lower()).first()
                
                if existing:
                    print(f"  ⊘ Skipped: '{word_data['word']}' (already exists)")
                    skipped_count += 1
                    continue
                
                # Fetch pronunciation data from Cambridge Dictionary
                print(f"  Fetching pronunciation for '{word_data['word']}'...")
                pronunciation_data = {'ipa_us': None, 'ipa_uk': None, 'audio_us': None, 'audio_uk': None}
                
                try:
                    pronunciation_data = fetch_pronunciation_data(word_data['word'])
                    if pronunciation_data and any(pronunciation_data.values()):
                        ipa_info = []
                        if pronunciation_data.get('ipa_uk'):
                            ipa_info.append(f"UK: /{pronunciation_data.get('ipa_uk')}/")
                        if pronunciation_data.get('ipa_us'):
                            ipa_info.append(f"US: /{pronunciation_data.get('ipa_us')}/")
                        if ipa_info:
                            print(f"    {', '.join(ipa_info)}")
                except Exception as e:
                    print(f"    ⚠ Could not fetch pronunciation: {str(e)[:50]}")
                
                # Create new vocabulary entry with random created date (past 60 days)
                new_word = Vocabulary(
                    word=word_data['word'].lower(),
                    definition=word_data['definition'],
                    example=word_data['example'],
                    translation=word_data.get('translation', ''),
                    ipa_us=pronunciation_data.get('ipa_us'),
                    ipa_uk=pronunciation_data.get('ipa_uk'),
                    audio_us=pronunciation_data.get('audio_us'),
                    audio_uk=pronunciation_data.get('audio_uk'),
                    status='learning',
                    created_at=datetime.now() - timedelta(days=random.randint(0, 60))
                )
                
                db.session.add(new_word)
                print(f"  ✓ Added: '{word_data['word']}'")
                added_count += 1
                
                # Add delay between requests to be polite to the server
                time.sleep(1)
        
        # Commit all changes
        db.session.commit()
        
        print("\n" + "=" * 70)
        print(f"✓ Successfully added {added_count} words")
        if skipped_count > 0:
            print(f"⊘ Skipped {skipped_count} words (already in database)")
        print(f"\nTotal words in database: {Vocabulary.query.count()}")
        print("\nBreakdown by level:")
        print(f"  B1: {len(vocabulary_data['B1'])} words")
        print(f"  B2: {len(vocabulary_data['B2'])} words")
        print(f"  C1: {len(vocabulary_data['C1'])} words")
        print(f"  Total: {sum(len(words) for words in vocabulary_data.values())} words")
        print("\nYou can now start the application with: python app.py")

if __name__ == '__main__':
    print("=" * 70)
    print("This script will fetch IPA pronunciation and audio from Cambridge Dictionary")
    print("⚠ Note: This requires internet access and may take several minutes")
    print("⚠ If you're behind a proxy, pronunciation fetching may fail (words will still be added)")
    print("=" * 70)
    print()
    populate_database()
